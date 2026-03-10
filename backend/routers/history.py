from fastapi import APIRouter, Query
from services import yfinance_service
from utils.cache import cache_history

router = APIRouter()

VALID_PERIODS = {"1wk", "1mo", "3mo", "6mo", "1y", "2y", "5y"}


@router.get("/{ticker}/history")
async def get_price_history(
    ticker: str,
    period: str = Query("1mo", description="yfinance period: 1wk 1mo 3mo 6mo 1y 2y 5y"),
):
    """OHLCV price history for a ticker. Used to render price charts."""
    if period not in VALID_PERIODS:
        period = "1mo"
    return await _cached_history(ticker.upper(), period)


@cache_history
async def _cached_history(ticker: str, period: str) -> list[dict]:
    return await yfinance_service.get_price_history(ticker, period)
