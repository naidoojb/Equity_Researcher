import yfinance as yf
import pandas as pd
from typing import Optional
from models.schemas import StockOverview, Fundamentals, Competitor


def _safe_float(val) -> Optional[float]:
    try:
        v = float(val)
        return None if (v != v) else v  # NaN check
    except (TypeError, ValueError):
        return None


def _safe_int(val) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def _fast_info_float(fi, attr: str) -> Optional[float]:
    """Safely read a float attribute from fast_info."""
    try:
        return _safe_float(getattr(fi, attr))
    except Exception:
        return None


async def get_overview(ticker: str) -> StockOverview:
    t = yf.Ticker(ticker.upper())

    # fast_info uses a lightweight Yahoo endpoint — much more reliable than t.info
    try:
        fi = t.fast_info
    except Exception:
        fi = None

    # History is also reliable (separate endpoint)
    try:
        hist = t.history(period="2d")
    except Exception:
        hist = pd.DataFrame()

    # t.info is the fragile one; wrap it and fall back to {} on any error
    try:
        info = t.info
        if not isinstance(info, dict):
            info = {}
    except Exception:
        info = {}

    # ── Price ──────────────────────────────────────────────────────────────
    price: float = 0.0
    if fi is not None:
        price = _fast_info_float(fi, "last_price") or price
    if not price and not hist.empty:
        price = _safe_float(hist["Close"].iloc[-1]) or 0.0
    # last resort: fall back to info fields
    if not price:
        price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice")) or 0.0

    # ── Previous close ─────────────────────────────────────────────────────
    prev_close: float = price  # default: no change
    if fi is not None:
        pc = _fast_info_float(fi, "previous_close")
        if pc:
            prev_close = pc
    if prev_close == price and len(hist) > 1:
        prev_close = _safe_float(hist["Close"].iloc[-2]) or price
    if prev_close == price:
        prev_close = _safe_float(
            info.get("previousClose") or info.get("regularMarketPreviousClose")
        ) or price

    change = round(price - prev_close, 4)
    change_pct = round(change / (prev_close or 1) * 100, 2)

    # ── Volume ─────────────────────────────────────────────────────────────
    volume: int = 0
    if fi is not None:
        volume = _safe_int(_fast_info_float(fi, "last_volume"))
    if not volume:
        volume = _safe_int(info.get("volume") or info.get("regularMarketVolume"))

    avg_volume: int = 0
    if fi is not None:
        avg_volume = _safe_int(_fast_info_float(fi, "three_month_average_volume"))
    if not avg_volume:
        avg_volume = _safe_int(info.get("averageVolume") or info.get("averageDailyVolume10Day"))

    # ── Market cap ─────────────────────────────────────────────────────────
    market_cap: Optional[float] = None
    if fi is not None:
        market_cap = _fast_info_float(fi, "market_cap")
    if market_cap is None:
        market_cap = _safe_float(info.get("marketCap"))

    # ── 52-week range ──────────────────────────────────────────────────────
    week_52_high: float = 0.0
    week_52_low: float = 0.0
    if fi is not None:
        week_52_high = _fast_info_float(fi, "year_high") or 0.0
        week_52_low = _fast_info_float(fi, "year_low") or 0.0
    if not week_52_high:
        week_52_high = _safe_float(info.get("fiftyTwoWeekHigh")) or 0.0
    if not week_52_low:
        week_52_low = _safe_float(info.get("fiftyTwoWeekLow")) or 0.0

    # ── Currency / exchange (fast_info is reliable here) ───────────────────
    currency: str = "USD"
    exchange: str = "N/A"
    if fi is not None:
        try:
            currency = fi.currency or info.get("currency", "USD")
            exchange = fi.exchange or info.get("exchange") or "N/A"
        except Exception:
            pass
    if currency == "USD" and info.get("currency"):
        currency = info["currency"]
    if exchange == "N/A":
        exchange = info.get("exchange") or info.get("fullExchangeName") or "N/A"

    # ── Name / sector / industry — only available via t.info ───────────────
    name: str = info.get("longName") or info.get("shortName") or ticker.upper()
    sector: Optional[str] = info.get("sector")
    industry: Optional[str] = info.get("industry")

    return StockOverview(
        ticker=ticker.upper(),
        name=name,
        price=price,
        change=change,
        change_pct=change_pct,
        volume=volume,
        avg_volume=avg_volume,
        market_cap=market_cap,
        week_52_high=week_52_high,
        week_52_low=week_52_low,
        currency=currency,
        exchange=exchange,
        sector=sector,
        industry=industry,
    )


async def get_fundamentals(ticker: str) -> Fundamentals:
    t = yf.Ticker(ticker.upper())

    # Wrap t.info — it can throw json.JSONDecodeError or network errors
    try:
        info = t.info
        if not isinstance(info, dict):
            info = {}
    except Exception:
        info = {}

    return Fundamentals(
        ticker=ticker.upper(),
        pe_ratio=_safe_float(info.get("trailingPE")),
        forward_pe=_safe_float(info.get("forwardPE")),
        eps=_safe_float(info.get("trailingEps")),
        revenue=_safe_float(info.get("totalRevenue")),
        revenue_growth=_safe_float(info.get("revenueGrowth")),
        gross_margin=_safe_float(info.get("grossMargins")),
        operating_margin=_safe_float(info.get("operatingMargins")),
        net_margin=_safe_float(info.get("profitMargins")),
        debt_to_equity=_safe_float(info.get("debtToEquity")),
        current_ratio=_safe_float(info.get("currentRatio")),
        dividend_yield=_safe_float(info.get("dividendYield")),
        book_value=_safe_float(info.get("bookValue")),
        price_to_book=_safe_float(info.get("priceToBook")),
        beta=_safe_float(info.get("beta")),
    )


async def get_price_history(ticker: str, period: str = "1mo") -> list[dict]:
    t = yf.Ticker(ticker.upper())
    try:
        hist = t.history(period=period)
    except Exception:
        return []
    if hist.empty:
        return []
    hist = hist.reset_index()
    return [
        {
            "date": row["Date"].strftime("%Y-%m-%d"),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "close": round(row["Close"], 2),
            "volume": int(row["Volume"]),
        }
        for _, row in hist.iterrows()
    ]


async def get_competitors(ticker: str) -> tuple[Optional[str], list[Competitor]]:
    t = yf.Ticker(ticker.upper())

    # Sector detection — wrap t.info
    try:
        info = t.info
        if not isinstance(info, dict):
            info = {}
    except Exception:
        info = {}

    sector = info.get("sector")

    peer_map = {
        "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AMZN", "CRM", "ORCL"],
        "Communication Services": ["META", "GOOGL", "NFLX", "SNAP", "DIS", "T"],
        "Consumer Cyclical": ["AMZN", "TSLA", "NKE", "HD", "MCD", "SBUX"],
        "Consumer Defensive": ["WMT", "PG", "KO", "PEP", "COST", "CL"],
        "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "MRK", "BMY", "GILD"],
        "Financials": ["JPM", "BAC", "WFC", "GS", "MS", "C", "BLK"],
        "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC"],
        "Industrials": ["HON", "UPS", "CAT", "BA", "GE", "MMM", "RTX"],
        "Basic Materials": ["LIN", "APD", "ECL", "SHW", "NEM", "FCX"],
        "Real Estate": ["AMT", "PLD", "CCI", "EQIX", "PSA", "O"],
        "Utilities": ["NEE", "DUK", "SO", "D", "AEP", "SRE"],
    }

    candidates = peer_map.get(sector or "", [])
    peers = [p for p in candidates if p != ticker.upper()][:5]

    results: list[Competitor] = []
    for peer in peers:
        try:
            pt = yf.Ticker(peer)

            # Use fast_info as the primary price source for peers too
            try:
                pfi = pt.fast_info
                price = _fast_info_float(pfi, "last_price") or 0.0
                prev = _fast_info_float(pfi, "previous_close") or price
                market_cap: Optional[float] = _fast_info_float(pfi, "market_cap")
            except Exception:
                price = 0.0
                prev = 0.0
                market_cap = None

            # t.info for name and P/E — wrap per peer
            try:
                pi = pt.info
                if not isinstance(pi, dict):
                    pi = {}
            except Exception:
                pi = {}

            # Fallback price from info if fast_info gave nothing
            if not price:
                price = _safe_float(pi.get("currentPrice") or pi.get("regularMarketPrice")) or 0.0
            if not prev:
                prev = _safe_float(pi.get("previousClose")) or price
            if market_cap is None:
                market_cap = _safe_float(pi.get("marketCap"))

            chg_pct = round((price - prev) / (prev or 1) * 100, 2)

            results.append(Competitor(
                ticker=peer,
                name=pi.get("longName") or pi.get("shortName") or peer,
                price=price,
                change_pct=chg_pct,
                market_cap=market_cap,
                pe_ratio=_safe_float(pi.get("trailingPE")),
            ))
        except Exception:
            continue

    return sector, results
