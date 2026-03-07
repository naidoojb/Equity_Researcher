from fastapi import APIRouter, HTTPException
from models.schemas import Fundamentals
from services import yfinance_service
from utils.cache import cache_fundamentals

router = APIRouter()


@router.get("/{ticker}/fundamentals", response_model=Fundamentals)
async def get_fundamentals(ticker: str):
    """Get fundamental financial metrics."""
    try:
        return await _cached_fundamentals(ticker.upper())
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@cache_fundamentals
async def _cached_fundamentals(ticker: str) -> Fundamentals:
    return await yfinance_service.get_fundamentals(ticker)
