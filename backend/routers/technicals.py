from fastapi import APIRouter, HTTPException
from models.schemas import TechnicalIndicators
from services import market_data_service
from utils.cache import cache_technicals

router = APIRouter()


@router.get("/{ticker}/technicals", response_model=TechnicalIndicators)
async def get_technicals(ticker: str):
    """Get RSI, MACD, moving averages, Bollinger Bands, EMA, volatility, and momentum."""
    try:
        return await _cached_technicals(ticker.upper())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@cache_technicals
async def _cached_technicals(ticker: str) -> TechnicalIndicators:
    return await market_data_service.get_technicals_with_fallback(ticker)
