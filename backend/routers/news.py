import asyncio
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from models.schemas import NewsItem, NewsResponse
from services import newsapi_service, yfinance_service
from utils.cache import cache_news
import anthropic

router = APIRouter()
_client = anthropic.Anthropic()


@router.get("/{ticker}/news", response_model=NewsResponse)
async def get_news(ticker: str):
    """Get news headlines with AI sentiment scoring."""
    try:
        return await _cached_news(ticker.upper())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@cache_news
async def _cached_news(ticker: str) -> NewsResponse:
    overview, raw_articles = await asyncio.gather(
        yfinance_service.get_overview(ticker),
        newsapi_service.get_news(ticker, limit=15),
    )

    scored = []
    for article in raw_articles:
        title = article.get("title", "")
        if not title or title == "[Removed]":
            continue

        sentiment, label = await _score_sentiment(title)
        scored.append(NewsItem(
            title=title,
            source=article.get("source", {}).get("name", "Unknown"),
            url=article.get("url", ""),
            published_at=article.get("publishedAt", ""),
            sentiment=sentiment,
            sentiment_label=label,
            summary=article.get("description"),
        ))

    avg_sentiment = (
        round(sum(a.sentiment for a in scored) / len(scored), 3)
        if scored else 0.0
    )

    return NewsResponse(ticker=ticker, articles=scored, avg_sentiment=avg_sentiment)


async def _score_sentiment(headline: str) -> tuple[float, str]:
    """Use Claude Haiku to quickly score headline sentiment (-1.0 to 1.0)."""
    try:
        response = _client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=20,
            messages=[{
                "role": "user",
                "content": (
                    f"Score this financial headline sentiment from -1.0 (very bearish) "
                    f"to 1.0 (very bullish). Reply with ONLY the number.\n\nHeadline: {headline}"
                ),
            }],
        )
        score_str = response.content[0].text.strip()
        score = max(-1.0, min(1.0, float(score_str)))
        if score > 0.1:
            label = "Positive"
        elif score < -0.1:
            label = "Negative"
        else:
            label = "Neutral"
        return round(score, 2), label
    except Exception:
        return 0.0, "Neutral"
