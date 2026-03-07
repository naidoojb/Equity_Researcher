from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from services.claude_service import generate_research_stream
from utils.cache import get_cached_research, set_cached_research
import json

router = APIRouter()


@router.get("/{ticker}/research")
async def get_research(ticker: str):
    """
    Stream a deep AI research report for a ticker via Server-Sent Events (SSE).

    The client should consume this as an EventSource stream.
    Event format: data: {"type": "text"|"thinking"|"tool_call"|"done", "content"?: "..."}
    """
    ticker = ticker.upper()

    # Check if we have a cached report for today
    cached = get_cached_research(ticker)
    if cached:
        async def cached_stream():
            # Replay cached report as a single chunk
            payload = json.dumps({"type": "text", "content": cached})
            yield f"data: {payload}\n\n"
            yield 'data: {"type":"done"}\n\n'
        return StreamingResponse(
            cached_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    async def stream_and_cache():
        full_text = []
        async for chunk in generate_research_stream(ticker):
            yield chunk
            # Collect text chunks for caching
            if chunk.startswith("data:"):
                try:
                    payload = json.loads(chunk[5:].strip())
                    if payload.get("type") == "text":
                        full_text.append(payload.get("content", ""))
                except Exception:
                    pass

        # Cache the complete report
        if full_text:
            set_cached_research(ticker, "".join(full_text))

    return StreamingResponse(
        stream_and_cache(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
