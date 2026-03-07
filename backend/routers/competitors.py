from fastapi import APIRouter, HTTPException
from models.schemas import CompetitorsResponse
from services import yfinance_service
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
    sector, competitors = await yfinance_service.get_competitors(ticker)
    return CompetitorsResponse(ticker=ticker, sector=sector, competitors=competitors)
