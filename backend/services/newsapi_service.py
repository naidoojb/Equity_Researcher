import os
import httpx
from typing import Optional

BASE_URL = "https://newsapi.org/v2/everything"


async def get_news(ticker: str, company_name: Optional[str] = None, limit: int = 20) -> list[dict]:
    """Fetch news articles for a ticker. Returns list of raw article dicts."""
    api_key = os.getenv("NEWSAPI_KEY", "")
    if not api_key:
        return _mock_news(ticker, limit)

    query = f'"{ticker}" OR "{company_name}"' if company_name else f'"{ticker}"'
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": limit,
        "apiKey": api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("articles", [])
    except Exception:
        return _mock_news(ticker, limit)


def _mock_news(ticker: str, limit: int) -> list[dict]:
    """Fallback mock news when API key is not configured."""
    from datetime import datetime, timedelta
    import random

    headlines = [
        f"{ticker} reports strong quarterly earnings, beating analyst expectations",
        f"Analysts upgrade {ticker} to 'Buy' citing strong fundamentals",
        f"{ticker} announces new product line, shares rise in pre-market trading",
        f"Institutional investors increase stakes in {ticker}",
        f"{ticker} faces regulatory scrutiny over recent acquisition",
        f"Market volatility impacts {ticker} amid macro uncertainty",
        f"{ticker} CEO discusses growth strategy in investor call",
        f"Supply chain improvements boost {ticker} margins, analysts say",
    ]

    articles = []
    for i in range(min(limit, len(headlines))):
        pub_date = (datetime.now() - timedelta(hours=i * 6)).isoformat() + "Z"
        articles.append({
            "title": headlines[i],
            "source": {"name": ["Reuters", "Bloomberg", "CNBC", "WSJ"][i % 4]},
            "url": f"https://example.com/news/{ticker.lower()}-{i}",
            "publishedAt": pub_date,
            "description": headlines[i],
        })
    return articles
