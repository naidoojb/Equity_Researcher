from fastapi import APIRouter, HTTPException
from models.schemas import CompetitorsResponse
from services import market_data_service
from utils.cache import cache_competitors

router = APIRouter()


@router.get("/{ticker}/competitors", response_model=CompetitorsResponse)
async def get_competitors(ticker: str):
    """Get sector peer comparison."""
    try:
        return await _cached_competitors(ticker.upper())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@cache_competitors
async def _cached_competitors(ticker: str) -> CompetitorsResponse:
    return await market_data_service.get_competitors_with_fallback(ticker)
