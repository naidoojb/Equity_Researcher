"""
Claude AI research engine.

Uses claude-opus-4-6 with adaptive thinking and tool_use to conduct
deep equity research. Tools give Claude real-time access to stock data,
news, technicals, and fundamentals during research generation.

The research report is streamed back via SSE.
"""
import os
import json
import uuid
import asyncio
from typing import AsyncGenerator
import anthropic
from services import market_data_service, newsapi_service, polygon_service

_client = anthropic.Anthropic()

MODEL = "claude-opus-4-6"

# ─── Tool definitions ─────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "get_stock_price",
        "description": (
            "Get the current stock price, daily change, volume, market cap, "
            "52-week high/low, sector, and industry for a ticker symbol."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol, e.g. AAPL"},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_technical_indicators",
        "description": (
            "Get technical analysis indicators: RSI, MACD, MACD signal line, "
            "MACD histogram, SMA-20, SMA-50, SMA-200, and Bollinger Bands."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_news_headlines",
        "description": "Get the latest news headlines for a stock ticker.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
                "limit": {"type": "integer", "description": "Number of headlines to fetch (max 20)", "default": 10},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_fundamentals",
        "description": (
            "Get fundamental financial data: P/E ratio, forward P/E, EPS, revenue, "
            "revenue growth, gross/operating/net margins, debt-to-equity, current ratio, "
            "dividend yield, book value, price-to-book, and beta."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_competitor_data",
        "description": "Get a list of sector peer companies with their price and key metrics for comparison.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_options_flow",
        "description": "Get options market data: put/call ratio and volume, which can indicate institutional sentiment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
            },
            "required": ["ticker"],
        },
    },
]

# ─── Tool executor ─────────────────────────────────────────────────────────────

async def execute_tool(name: str, inputs: dict) -> str:
    """Execute a tool call and return JSON string result."""
    ticker = inputs.get("ticker", "").upper()

    try:
        if name == "get_stock_price":
            overview = await market_data_service.get_overview_with_fallback(ticker)
            return json.dumps(overview.model_dump(), default=str)

        elif name == "get_technical_indicators":
            technicals = await market_data_service.get_technicals_with_fallback(ticker)
            return json.dumps(technicals.model_dump(), default=str)

        elif name == "get_news_headlines":
            limit = min(int(inputs.get("limit", 10)), 20)
            articles = await newsapi_service.get_news(ticker, limit=limit)
            headlines = [
                {"title": a.get("title"), "source": a.get("source", {}).get("name"),
                 "published_at": a.get("publishedAt")}
                for a in articles if a.get("title") and a.get("title") != "[Removed]"
            ]
            return json.dumps({"headlines": headlines})

        elif name == "get_fundamentals":
            fundamentals = await market_data_service.get_fundamentals_with_fallback(ticker)
            return json.dumps(fundamentals.model_dump(), default=str)

        elif name == "get_competitor_data":
            comp = await market_data_service.get_competitors_with_fallback(ticker)
            return json.dumps(comp.model_dump(), default=str)

        elif name == "get_options_flow":
            flow = await polygon_service.get_options_flow(ticker)
            return json.dumps(flow or {"note": "Options data not available"})

        else:
            return json.dumps({"error": f"Unknown tool: {name}"})

    except Exception as e:
        return json.dumps({"error": str(e)})


# ─── Research generator ────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior equity research analyst at a top-tier investment bank.
Your research reports are comprehensive, data-driven, and actionable.

When asked to research a stock:
1. Use your tools to gather: current price & momentum, technical signals, latest news,
   fundamental valuation, and competitor positioning.
2. Structure your report with clear sections using markdown headers.
3. Be specific with numbers — cite actual values from the data you retrieve.
4. Provide a clear investment thesis with both bull and bear cases.
5. End with a definitive Daily Signal Rating: STRONG BUY / BUY / HOLD / SELL / STRONG SELL
   with a confidence score (0–100%) and a brief rationale.

Report structure:
## Executive Summary
## Price & Market Overview
## Technical Analysis
## News Sentiment & Catalysts
## Fundamental Analysis
## Competitive Positioning
## Bull Case
## Bear Case
## Key Risks
## Daily Signal Rating"""


async def generate_research_stream(ticker: str) -> AsyncGenerator[str, None]:
    """
    Stream a deep research report for a ticker using Claude with tool_use.
    Yields SSE-formatted text chunks.
    """
    messages = [{
        "role": "user",
        "content": (
            f"Please conduct a comprehensive equity research report for **{ticker.upper()}**. "
            f"Use all available tools to gather real-time data before writing your analysis. "
            f"Today's date is {__import__('datetime').date.today().isoformat()}."
        ),
    }]

    # Track all tool_use IDs used across the entire conversation to prevent duplicates
    seen_tool_use_ids: set[str] = set()

    # Agentic loop: Claude fetches data via tools, then generates the report
    while True:
        with _client.messages.stream(
            model=MODEL,
            max_tokens=8000,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        ) as stream:
            collected_content = []
            current_text = ""

            for event in stream:
                if event.type == "content_block_start":
                    if event.content_block.type == "text":
                        current_text = ""
                    elif event.content_block.type == "thinking":
                        # Emit thinking progress indicator
                        yield "data: {\"type\":\"thinking\"}\n\n"

                elif event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        chunk = event.delta.text
                        current_text += chunk
                        # Stream text chunks to client
                        payload = json.dumps({"type": "text", "content": chunk})
                        yield f"data: {payload}\n\n"
                    elif event.delta.type == "input_json_delta":
                        pass  # Tool input being built

                elif event.type == "content_block_stop":
                    pass

            final_message = stream.get_final_message()

            # Convert SDK objects to plain dicts and deduplicate tool_use IDs.
            # Claude can rarely return the same tool_use ID across iterations,
            # which causes a 400 "tool_use ids must be unique" API error.
            content_list = []
            for block in final_message.content:
                block_dict = block.model_dump()
                if block_dict.get("type") == "tool_use":
                    if block_dict["id"] in seen_tool_use_ids:
                        block_dict["id"] = f"toolu_{uuid.uuid4().hex}"
                    seen_tool_use_ids.add(block_dict["id"])
                content_list.append(block_dict)

            messages.append({"role": "assistant", "content": content_list})

            # If Claude is done (no tool calls), end the stream
            if final_message.stop_reason == "end_turn":
                yield "data: {\"type\":\"done\"}\n\n"
                break

            # Execute tool calls and continue the loop
            if final_message.stop_reason == "tool_use":
                tool_results = []
                tool_blocks = [b for b in content_list if b.get("type") == "tool_use"]

                # Notify client which tools are being called
                for block in tool_blocks:
                    tool_notif = json.dumps({"type": "tool_call", "tool": block["name"]})
                    yield f"data: {tool_notif}\n\n"

                # Execute all tool calls concurrently
                results = await asyncio.gather(*[
                    execute_tool(block["name"], block["input"])
                    for block in tool_blocks
                ])

                for block, result in zip(tool_blocks, results):
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": result,
                    })

                messages.append({"role": "user", "content": tool_results})
                # Continue loop — Claude will now write the report
            else:
                # Unexpected stop reason
                yield "data: {\"type\":\"done\"}\n\n"
                break
