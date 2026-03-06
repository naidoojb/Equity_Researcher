import asyncio
from fastapi import APIRouter, HTTPException
from models.schemas import TechnicalIndicators, Signal
from services import alphavantage_service, yfinance_service
from utils.cache import cache_technicals

router = APIRouter()


@router.get("/{ticker}/technicals", response_model=TechnicalIndicators)
async def get_technicals(ticker: str):
    """Get RSI, MACD, moving averages, and Bollinger Bands."""
    try:
        return await _cached_technicals(ticker.upper())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@cache_technicals
async def _cached_technicals(ticker: str) -> TechnicalIndicators:
    # Fetch overview for current price
    overview, (rsi, (macd, macd_sig, macd_hist), sma_20, sma_50, sma_200, (bb_upper, bb_mid, bb_lower)) = (
        await asyncio.gather(
            yfinance_service.get_overview(ticker),
            _fetch_all_technicals(ticker),
        )
    )

    price = overview.price
    signals: list[Signal] = []

    # RSI signals
    if rsi is not None:
        if rsi < 30:
            signals.append(Signal(label="RSI", value=f"{rsi:.1f}", direction="bullish"))
        elif rsi > 70:
            signals.append(Signal(label="RSI", value=f"{rsi:.1f}", direction="bearish"))
        else:
            signals.append(Signal(label="RSI", value=f"{rsi:.1f}", direction="neutral"))

    # MACD signal
    if macd is not None and macd_hist is not None:
        direction = "bullish" if macd_hist > 0 else "bearish"
        signals.append(Signal(label="MACD", value=f"{macd:.4f}", direction=direction))

    # Price vs SMA200
    if sma_200 is not None:
        direction = "bullish" if price > sma_200 else "bearish"
        signals.append(Signal(
            label="Price vs SMA200",
            value=f"${price:.2f} vs ${sma_200:.2f}",
            direction=direction,
        ))

    # Price vs SMA50
    if sma_50 is not None:
        direction = "bullish" if price > sma_50 else "bearish"
        signals.append(Signal(
            label="Price vs SMA50",
            value=f"${price:.2f} vs ${sma_50:.2f}",
            direction=direction,
        ))

    return TechnicalIndicators(
        ticker=ticker,
        rsi=rsi,
        macd=macd,
        macd_signal=macd_sig,
        macd_hist=macd_hist,
        sma_20=sma_20,
        sma_50=sma_50,
        sma_200=sma_200,
        bb_upper=bb_upper,
        bb_lower=bb_lower,
        bb_middle=bb_mid,
        price=price,
        signals=signals,
    )


async def _fetch_all_technicals(ticker: str):
    return await asyncio.gather(
        alphavantage_service.get_rsi(ticker),
        _get_macd(ticker),
        alphavantage_service.get_sma(ticker, 20),
        alphavantage_service.get_sma(ticker, 50),
        alphavantage_service.get_sma(ticker, 200),
        _get_bbands(ticker),
    )


async def _get_macd(ticker: str):
    return await alphavantage_service.get_macd(ticker)


async def _get_bbands(ticker: str):
    return await alphavantage_service.get_bbands(ticker)
