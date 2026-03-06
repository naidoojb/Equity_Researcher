import os
import httpx
from typing import Optional

BASE_URL = "https://www.alphavantage.co/query"


async def _fetch(params: dict) -> dict:
    api_key = os.getenv("ALPHAVANTAGE_KEY", "demo")
    params["apikey"] = api_key
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(BASE_URL, params=params)
        resp.raise_for_status()
        return resp.json()


async def get_rsi(ticker: str, interval: str = "daily", time_period: int = 14) -> Optional[float]:
    try:
        data = await _fetch({
            "function": "RSI",
            "symbol": ticker.upper(),
            "interval": interval,
            "time_period": time_period,
            "series_type": "close",
        })
        values = data.get("Technical Analysis: RSI", {})
        if not values:
            return None
        latest_key = sorted(values.keys(), reverse=True)[0]
        return round(float(values[latest_key]["RSI"]), 2)
    except Exception:
        return None


async def get_macd(ticker: str) -> tuple[Optional[float], Optional[float], Optional[float]]:
    """Returns (macd, signal, hist)"""
    try:
        data = await _fetch({
            "function": "MACD",
            "symbol": ticker.upper(),
            "interval": "daily",
            "series_type": "close",
        })
        values = data.get("Technical Analysis: MACD", {})
        if not values:
            return None, None, None
        latest_key = sorted(values.keys(), reverse=True)[0]
        row = values[latest_key]
        return (
            round(float(row["MACD"]), 4),
            round(float(row["MACD_Signal"]), 4),
            round(float(row["MACD_Hist"]), 4),
        )
    except Exception:
        return None, None, None


async def get_sma(ticker: str, time_period: int = 20) -> Optional[float]:
    try:
        data = await _fetch({
            "function": "SMA",
            "symbol": ticker.upper(),
            "interval": "daily",
            "time_period": time_period,
            "series_type": "close",
        })
        key = f"Technical Analysis: SMA"
        values = data.get(key, {})
        if not values:
            return None
        latest_key = sorted(values.keys(), reverse=True)[0]
        return round(float(values[latest_key]["SMA"]), 4)
    except Exception:
        return None


async def get_bbands(ticker: str) -> tuple[Optional[float], Optional[float], Optional[float]]:
    """Returns (upper, middle, lower)"""
    try:
        data = await _fetch({
            "function": "BBANDS",
            "symbol": ticker.upper(),
            "interval": "daily",
            "time_period": 20,
            "series_type": "close",
        })
        values = data.get("Technical Analysis: BBANDS", {})
        if not values:
            return None, None, None
        latest_key = sorted(values.keys(), reverse=True)[0]
        row = values[latest_key]
        return (
            round(float(row["Real Upper Band"]), 4),
            round(float(row["Real Middle Band"]), 4),
            round(float(row["Real Lower Band"]), 4),
        )
    except Exception:
        return None, None, None
