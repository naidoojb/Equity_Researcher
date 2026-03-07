from fastapi import APIRouter, HTTPException
from models.schemas import SignalsResponse
from services import market_data_service
from utils.cache import cache_signals

router = APIRouter()


@router.get("/{ticker}/signals", response_model=SignalsResponse)
async def get_signals(ticker: str):
    """Get aggregated daily bull/bear signals with composite score."""
    try:
        return await _cached_signals(ticker.upper())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@cache_signals
async def _cached_signals(ticker: str) -> SignalsResponse:
    return await market_data_service.get_signals_with_fallback(ticker)
