from fastapi import APIRouter, Query
from models.schemas import SearchResult
import yfinance as yf

router = APIRouter()

# Curated list of popular tickers for quick search
POPULAR_TICKERS = [
    ("AAPL", "Apple Inc.", "NASDAQ", "Technology"),
    ("MSFT", "Microsoft Corporation", "NASDAQ", "Technology"),
    ("GOOGL", "Alphabet Inc.", "NASDAQ", "Communication Services"),
    ("AMZN", "Amazon.com Inc.", "NASDAQ", "Consumer Cyclical"),
    ("NVDA", "NVIDIA Corporation", "NASDAQ", "Technology"),
    ("TSLA", "Tesla Inc.", "NASDAQ", "Consumer Cyclical"),
    ("META", "Meta Platforms Inc.", "NASDAQ", "Communication Services"),
    ("BRK-B", "Berkshire Hathaway", "NYSE", "Financials"),
    ("JPM", "JPMorgan Chase", "NYSE", "Financials"),
    ("UNH", "UnitedHealth Group", "NYSE", "Healthcare"),
    ("JNJ", "Johnson & Johnson", "NYSE", "Healthcare"),
    ("XOM", "ExxonMobil Corporation", "NYSE", "Energy"),
    ("V", "Visa Inc.", "NYSE", "Financials"),
    ("PG", "Procter & Gamble", "NYSE", "Consumer Defensive"),
    ("MA", "Mastercard Inc.", "NYSE", "Financials"),
    ("HD", "Home Depot Inc.", "NYSE", "Consumer Cyclical"),
    ("CVX", "Chevron Corporation", "NYSE", "Energy"),
    ("LLY", "Eli Lilly and Company", "NYSE", "Healthcare"),
    ("ABBV", "AbbVie Inc.", "NYSE", "Healthcare"),
    ("BAC", "Bank of America", "NYSE", "Financials"),
]


@router.get("/search", response_model=list[SearchResult])
async def search_tickers(q: str = Query(..., min_length=1)):
    """Search for tickers by symbol or company name."""
    q_upper = q.upper()
    q_lower = q.lower()

    results = [
        SearchResult(ticker=t, name=n, exchange=ex, sector=sec)
        for t, n, ex, sec in POPULAR_TICKERS
        if q_upper in t or q_lower in n.lower()
    ]

    # If no match in popular list, try yfinance directly
    if not results and len(q) >= 2:
        try:
            ticker_obj = yf.Ticker(q.upper())
            info = ticker_obj.info
            if info.get("longName") or info.get("shortName"):
                results = [SearchResult(
                    ticker=q.upper(),
                    name=info.get("longName") or info.get("shortName") or q.upper(),
                    exchange=info.get("exchange") or "N/A",
                    sector=info.get("sector"),
                )]
        except Exception:
            pass

    return results[:10]
