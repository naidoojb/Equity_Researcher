import os
import asyncio
from typing import Optional, Any

import httpx

from models.schemas import StockOverview, Fundamentals, TechnicalIndicators

BASE_URL = "https://www.alphavantage.co/query"


def has_configured_api_key() -> bool:
    api_key = os.getenv("ALPHAVANTAGE_KEY", "").strip()
    return bool(api_key and api_key.lower() != "demo")


async def _fetch(params: dict) -> dict:
    api_key = os.getenv("ALPHAVANTAGE_KEY", "demo")
    params["apikey"] = api_key
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    if isinstance(data, dict):
        if data.get("Error Message"):
            raise ValueError(data["Error Message"])
        if data.get("Information"):
            raise ValueError(data["Information"])
        if data.get("Note"):
            raise ValueError(data["Note"])

    return data


def _safe_float(val: Any) -> Optional[float]:
    try:
        parsed = float(val)
        return None if parsed != parsed else parsed
    except (TypeError, ValueError):
        return None


def _safe_int(val: Any) -> int:
    try:
        return int(float(val))
    except (TypeError, ValueError):
        return 0


async def get_quote(ticker: str) -> dict:
    return await _fetch({"function": "GLOBAL_QUOTE", "symbol": ticker.upper()})


async def get_company_overview(ticker: str) -> dict:
    return await _fetch({"function": "OVERVIEW", "symbol": ticker.upper()})


async def get_income_statement(ticker: str) -> dict:
    return await _fetch({"function": "INCOME_STATEMENT", "symbol": ticker.upper()})


async def get_balance_sheet(ticker: str) -> dict:
    return await _fetch({"function": "BALANCE_SHEET", "symbol": ticker.upper()})


async def map_stock_overview(ticker: str) -> StockOverview:
    quote_resp, company = await asyncio.gather(get_quote(ticker), get_company_overview(ticker))
    quote = quote_resp.get("Global Quote", {}) if isinstance(quote_resp, dict) else {}

    price = _safe_float(quote.get("05. price")) or 0
    previous_close = _safe_float(quote.get("08. previous close"))
    change = _safe_float(quote.get("09. change"))
    change_pct_raw = str(quote.get("10. change percent", "")).replace("%", "")
    change_pct = _safe_float(change_pct_raw)

    if change is None and previous_close is not None:
        change = round(price - previous_close, 2)
    if change_pct is None and previous_close not in (None, 0):
        change_pct = round(((price - previous_close) / previous_close) * 100, 2)

    return StockOverview(
        ticker=ticker.upper(),
        name=company.get("Name") or ticker.upper(),
        exchange=company.get("Exchange") or "N/A",
        sector=company.get("Sector"),
        industry=company.get("Industry"),
        price=price,
        previous_close=previous_close,
        change=change or 0,
        change_pct=change_pct or 0,
        market_cap=_safe_float(company.get("MarketCapitalization")) or None,
        currency=company.get("Currency") or "USD",
        week_52_high=_safe_float(company.get("52WeekHigh")) or price,
        week_52_low=_safe_float(company.get("52WeekLow")) or price,
        volume=_safe_int(quote.get("06. volume")),
        avg_volume=_safe_int(company.get("SharesOutstanding")),
    )


async def map_fundamentals(ticker: str) -> Fundamentals:
    overview, income, balance = await asyncio.gather(
        get_company_overview(ticker),
        get_income_statement(ticker),
        get_balance_sheet(ticker),
    )

    annual_income = ((income or {}).get("annualReports") or [{}])[0]
    annual_balance = ((balance or {}).get("annualReports") or [{}])[0]

    revenue = _safe_float(annual_income.get("totalRevenue"))
    gross_profit = _safe_float(annual_income.get("grossProfit"))
    operating_income = _safe_float(annual_income.get("operatingIncome"))
    net_income = _safe_float(annual_income.get("netIncome"))
    total_liabilities = _safe_float(annual_balance.get("totalLiabilities"))
    shareholder_equity = _safe_float(annual_balance.get("totalShareholderEquity"))
    current_assets = _safe_float(annual_balance.get("totalCurrentAssets"))
    current_liabilities = _safe_float(annual_balance.get("totalCurrentLiabilities"))

    gross_margin = (gross_profit / revenue) if gross_profit is not None and revenue not in (None, 0) else None
    operating_margin = (operating_income / revenue) if operating_income is not None and revenue not in (None, 0) else None
    net_margin = (net_income / revenue) if net_income is not None and revenue not in (None, 0) else None
    debt_to_equity = (total_liabilities / shareholder_equity) if total_liabilities is not None and shareholder_equity not in (None, 0) else None
    current_ratio = (current_assets / current_liabilities) if current_assets is not None and current_liabilities not in (None, 0) else None

    return Fundamentals(
        ticker=ticker.upper(),
        pe_ratio=_safe_float(overview.get("PERatio")),
        forward_pe=None,
        eps=_safe_float(overview.get("EPS")),
        revenue=revenue,
        revenue_growth=_safe_float(overview.get("QuarterlyRevenueGrowthYOY")),
        gross_margin=gross_margin,
        operating_margin=operating_margin,
        net_margin=net_margin,
        debt_to_equity=debt_to_equity,
        current_ratio=current_ratio,
        dividend_yield=_safe_float(overview.get("DividendYield")),
        beta=_safe_float(overview.get("Beta")),
        book_value=_safe_float(overview.get("BookValue")),
        price_to_book=_safe_float(overview.get("PriceToBookRatio")),
        roe=_safe_float(overview.get("ReturnOnEquityTTM")),
    )


async def map_technicals(ticker: str, price: float = 0) -> TechnicalIndicators:
    rsi, (macd, macd_signal, macd_hist), sma_20, sma_50, sma_200, ema_20, (bb_upper, bb_middle, bb_lower) = (
        await asyncio.gather(
            get_rsi(ticker),
            get_macd(ticker),
            get_sma(ticker, 20),
            get_sma(ticker, 50),
            get_sma(ticker, 200),
            get_ema(ticker, 20),
            get_bbands(ticker),
        )
    )

    bb_position = None
    if bb_upper is not None and bb_lower is not None and bb_upper != bb_lower and price is not None:
        bb_position = round((price - bb_lower) / (bb_upper - bb_lower) * 100, 1)

    return TechnicalIndicators(
        ticker=ticker.upper(),
        price=price or 0,
        rsi=rsi,
        macd=macd,
        macd_signal=macd_signal,
        macd_hist=macd_hist,
        sma_20=sma_20,
        sma_50=sma_50,
        sma_200=sma_200,
        ema_20=ema_20,
        bb_upper=bb_upper,
        bb_middle=bb_middle,
        bb_lower=bb_lower,
        bb_position=bb_position,
        volatility=None,
        momentum_5d=None,
        momentum_20d=None,
        signals=[],
    )


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
        values = data.get("Technical Analysis: SMA", {})
        if not values:
            return None
        latest_key = sorted(values.keys(), reverse=True)[0]
        return round(float(values[latest_key]["SMA"]), 4)
    except Exception:
        return None


async def get_ema(ticker: str, time_period: int = 20) -> Optional[float]:
    try:
        data = await _fetch({
            "function": "EMA",
            "symbol": ticker.upper(),
            "interval": "daily",
            "time_period": time_period,
            "series_type": "close",
        })
        values = data.get("Technical Analysis: EMA", {})
        if not values:
            return None
        latest_key = sorted(values.keys(), reverse=True)[0]
        return round(float(values[latest_key]["EMA"]), 4)
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
