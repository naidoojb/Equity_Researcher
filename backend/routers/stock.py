from fastapi import APIRouter, HTTPException
from models.schemas import StockOverview
from services import yfinance_service
from utils.cache import cache_overview

router = APIRouter()


@router.get("/{ticker}", response_model=StockOverview)
async def get_stock_overview(ticker: str):
    """Get stock price, volume, market cap, and basic info."""
    try:
        return await _cached_overview(ticker.upper())
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found: {str(e)}")


@cache_overview
async def _cached_overview(ticker: str) -> StockOverview:
    return await yfinance_service.get_overview(ticker)
