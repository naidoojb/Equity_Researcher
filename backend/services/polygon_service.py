import os
import httpx
from typing import Optional

BASE_URL = "https://api.polygon.io"


async def get_realtime_quote(ticker: str) -> Optional[dict]:
    """Get real-time quote snapshot from Polygon.io."""
    api_key = os.getenv("POLYGON_API_KEY", "")
    if not api_key:
        return None

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BASE_URL}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker.upper()}",
                params={"apiKey": api_key},
            )
            resp.raise_for_status()
            data = resp.json()
            ticker_data = data.get("ticker", {})
            day = ticker_data.get("day", {})
            prev = ticker_data.get("prevDay", {})
            return {
                "open": day.get("o"),
                "high": day.get("h"),
                "low": day.get("l"),
                "close": day.get("c"),
                "volume": day.get("v"),
                "vwap": day.get("vw"),
                "prev_close": prev.get("c"),
            }
    except Exception:
        return None


async def get_options_flow(ticker: str) -> Optional[dict]:
    """Get options summary — put/call ratio and notable contracts."""
    api_key = os.getenv("POLYGON_API_KEY", "")
    if not api_key:
        return None

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BASE_URL}/v3/snapshot/options/{ticker.upper()}",
                params={"apiKey": api_key, "limit": 10},
            )
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            if not results:
                return None

            calls = [r for r in results if r.get("details", {}).get("contract_type") == "call"]
            puts = [r for r in results if r.get("details", {}).get("contract_type") == "put"]
            call_vol = sum(r.get("day", {}).get("volume", 0) for r in calls)
            put_vol = sum(r.get("day", {}).get("volume", 0) for r in puts)

            return {
                "call_volume": call_vol,
                "put_volume": put_vol,
                "put_call_ratio": round(put_vol / call_vol, 2) if call_vol > 0 else None,
                "total_contracts": len(results),
            }
    except Exception:
        return None
