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


async def get_overview(ticker: str) -> StockOverview:
    t = yf.Ticker(ticker.upper())
    info = t.info
    hist = t.history(period="2d")

    price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice") or
                        (hist["Close"].iloc[-1] if not hist.empty else 0))
    prev_close = _safe_float(info.get("previousClose") or info.get("regularMarketPreviousClose") or
                             (hist["Close"].iloc[-2] if len(hist) > 1 else price))

    change = round((price or 0) - (prev_close or 0), 4)
    change_pct = round(change / (prev_close or 1) * 100, 2)

    return StockOverview(
        ticker=ticker.upper(),
        name=info.get("longName") or info.get("shortName") or ticker.upper(),
        price=price or 0.0,
        change=change,
        change_pct=change_pct,
        volume=_safe_int(info.get("volume") or info.get("regularMarketVolume")),
        avg_volume=_safe_int(info.get("averageVolume") or info.get("averageDailyVolume10Day")),
        market_cap=_safe_float(info.get("marketCap")),
        week_52_high=_safe_float(info.get("fiftyTwoWeekHigh")) or 0.0,
        week_52_low=_safe_float(info.get("fiftyTwoWeekLow")) or 0.0,
        currency=info.get("currency", "USD"),
        exchange=info.get("exchange") or info.get("fullExchangeName") or "N/A",
        sector=info.get("sector"),
        industry=info.get("industry"),
    )


async def get_fundamentals(ticker: str) -> Fundamentals:
    t = yf.Ticker(ticker.upper())
    info = t.info

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
    hist = t.history(period=period)
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
    info = t.info
    sector = info.get("sector")

    # Use recommended tickers from yfinance if available
    peers: list[str] = []
    try:
        recs = t.recommendations
        if recs is not None and not recs.empty:
            peers = []  # recommendations is analyst ratings, not peers
    except Exception:
        pass

    # Fall back to known sector ETF constituents / hardcoded peers per sector
    peer_map = {
        "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AMZN", "CRM", "ORCL"],
        "Communication Services": ["META", "GOOGL", "NFLX", "SNAP", "TWTR", "DIS"],
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
            pi = pt.info
            price = _safe_float(pi.get("currentPrice") or pi.get("regularMarketPrice")) or 0.0
            prev = _safe_float(pi.get("previousClose")) or price
            chg_pct = round((price - prev) / (prev or 1) * 100, 2)
            results.append(Competitor(
                ticker=peer,
                name=pi.get("longName") or pi.get("shortName") or peer,
                price=price,
                change_pct=chg_pct,
                market_cap=_safe_float(pi.get("marketCap")),
                pe_ratio=_safe_float(pi.get("trailingPE")),
            ))
        except Exception:
            continue

    return sector, results
