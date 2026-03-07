import math
import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, List

from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands

from models.schemas import (
    StockOverview,
    Fundamentals,
    TechnicalIndicators,
    Signal,
    SignalsResponse,
    Competitor,
    CompetitorsResponse,
)


def _safe_float(val) -> Optional[float]:
    try:
        v = float(val)
        return None if v != v else v
    except (TypeError, ValueError):
        return None


def _safe_int(val) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def _safe_dict(obj: Any) -> Dict[str, Any]:
    return obj if isinstance(obj, dict) else {}


def _safe_history(ticker_obj: yf.Ticker, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    try:
        hist = ticker_obj.history(period=period, interval=interval, auto_adjust=False)
        if hist is None or hist.empty:
            return pd.DataFrame()
        return hist
    except Exception:
        return pd.DataFrame()


def _safe_info(ticker_obj: yf.Ticker) -> Dict[str, Any]:
    try:
        info = ticker_obj.info
        return info if isinstance(info, dict) else {}
    except Exception:
        return {}


def _fast_info_value(fast_info: Any, key: str) -> Any:
    try:
        if hasattr(fast_info, "get"):
            return fast_info.get(key)
        return getattr(fast_info, key, None)
    except Exception:
        return None


def _fast_info_float(fast_info: Any, key: str) -> Optional[float]:
    return _safe_float(_fast_info_value(fast_info, key))


def _latest_close(hist: pd.DataFrame) -> Optional[float]:
    if hist is not None and not hist.empty and "Close" in hist.columns:
        return _safe_float(hist["Close"].iloc[-1])
    return None


def _previous_close(hist: pd.DataFrame) -> Optional[float]:
    if hist is not None and not hist.empty and "Close" in hist.columns and len(hist) > 1:
        return _safe_float(hist["Close"].iloc[-2])
    return None


def _compute_technicals_from_history(ticker: str, hist: pd.DataFrame) -> TechnicalIndicators:
    if hist is None or hist.empty or "Close" not in hist.columns:
        return TechnicalIndicators(
            ticker=ticker.upper(),
            price=0,
            rsi=None,
            macd=None,
            macd_signal=None,
            macd_hist=None,
            sma_20=None,
            sma_50=None,
            sma_200=None,
            ema_20=None,
            bb_upper=None,
            bb_middle=None,
            bb_lower=None,
            bb_position=None,
            volatility=None,
            momentum_5d=None,
            momentum_20d=None,
            signals=[],
        )

    close = hist["Close"].astype(float)

    price = _safe_float(close.iloc[-1]) or 0

    rsi = None
    macd_val = None
    macd_signal = None
    macd_hist_val = None
    sma_20 = None
    sma_50 = None
    sma_200 = None
    ema_20 = None
    bb_upper = None
    bb_middle = None
    bb_lower = None
    bb_position = None
    volatility = None
    momentum_5d = None
    momentum_20d = None

    try:
        if len(close) >= 14:
            rsi = _safe_float(RSIIndicator(close=close, window=14).rsi().iloc[-1])
    except Exception:
        pass

    try:
        if len(close) >= 26:
            macd_obj = MACD(close=close)
            macd_val = _safe_float(macd_obj.macd().iloc[-1])
            macd_signal = _safe_float(macd_obj.macd_signal().iloc[-1])
            macd_hist_val = _safe_float(macd_obj.macd_diff().iloc[-1])
    except Exception:
        pass

    try:
        if len(close) >= 20:
            sma_20 = _safe_float(SMAIndicator(close=close, window=20).sma_indicator().iloc[-1])
            ema_20 = _safe_float(EMAIndicator(close=close, window=20).ema_indicator().iloc[-1])
            bb = BollingerBands(close=close, window=20, window_dev=2)
            bb_upper = _safe_float(bb.bollinger_hband().iloc[-1])
            bb_middle = _safe_float(bb.bollinger_mavg().iloc[-1])
            bb_lower = _safe_float(bb.bollinger_lband().iloc[-1])

            # Fix 5: scale to 0–100 (not 0–1)
            if bb_upper is not None and bb_lower is not None and price is not None and bb_upper != bb_lower:
                bb_position = round((price - bb_lower) / (bb_upper - bb_lower) * 100, 1)
    except Exception:
        pass

    try:
        if len(close) >= 50:
            sma_50 = _safe_float(SMAIndicator(close=close, window=50).sma_indicator().iloc[-1])
    except Exception:
        pass

    try:
        if len(close) >= 200:
            sma_200 = _safe_float(SMAIndicator(close=close, window=200).sma_indicator().iloc[-1])
    except Exception:
        pass

    try:
        returns = close.pct_change().dropna()
        if not returns.empty:
            volatility = _safe_float(returns.tail(20).std() * (252 ** 0.5))
    except Exception:
        pass

    try:
        if len(close) > 5:
            old = _safe_float(close.iloc[-6])
            if old and old != 0:
                momentum_5d = round(((price - old) / old) * 100, 2)
    except Exception:
        pass

    try:
        if len(close) > 20:
            old = _safe_float(close.iloc[-21])
            if old and old != 0:
                momentum_20d = round(((price - old) / old) * 100, 2)
    except Exception:
        pass

    return TechnicalIndicators(
        ticker=ticker.upper(),
        price=price,
        rsi=rsi,
        macd=macd_val,
        macd_signal=macd_signal,
        macd_hist=macd_hist_val,
        sma_20=sma_20,
        sma_50=sma_50,
        sma_200=sma_200,
        ema_20=ema_20,
        bb_upper=bb_upper,
        bb_middle=bb_middle,
        bb_lower=bb_lower,
        bb_position=bb_position,
        volatility=volatility,
        momentum_5d=momentum_5d,
        momentum_20d=momentum_20d,
        signals=[],
    )


async def get_overview(ticker: str) -> StockOverview:
    t = yf.Ticker(ticker.upper())

    try:
        fast = getattr(t, "fast_info", {}) or {}
    except Exception:
        fast = {}

    info = _safe_info(t)
    hist = _safe_history(t, period="1y", interval="1d")

    price = (
        _fast_info_float(fast, "lastPrice")
        or _safe_float(info.get("currentPrice"))
        or _latest_close(hist)
        or 0
    )

    previous_close = (
        _fast_info_float(fast, "previousClose")
        or _safe_float(info.get("previousClose"))
        or _previous_close(hist)
    )

    change = round((price or 0) - (previous_close or 0), 2) if previous_close is not None else 0
    change_pct = round((change / previous_close) * 100, 2) if previous_close not in (None, 0) else 0

    week_52_high = (
        _fast_info_float(fast, "yearHigh")
        or _safe_float(info.get("fiftyTwoWeekHigh"))
    )
    week_52_low = (
        _fast_info_float(fast, "yearLow")
        or _safe_float(info.get("fiftyTwoWeekLow"))
    )

    volume = (
        _safe_int(_fast_info_value(fast, "lastVolume"))
        or _safe_int(info.get("volume"))
    )
    # Fix 1: schema field is avg_volume (not average_volume)
    avg_volume = (
        _safe_int(_fast_info_value(fast, "tenDayAverageVolume"))
        or _safe_int(info.get("averageVolume"))
    )

    market_cap = (
        _safe_int(_fast_info_value(fast, "marketCap"))
        or _safe_int(info.get("marketCap"))
    )

    return StockOverview(
        ticker=ticker.upper(),
        name=info.get("shortName") or info.get("longName") or ticker.upper(),
        exchange=info.get("exchange") or _fast_info_value(fast, "exchange") or "N/A",
        sector=info.get("sector"),
        industry=info.get("industry"),
        price=price,
        previous_close=previous_close,
        change=change,
        change_pct=change_pct,
        market_cap=market_cap if market_cap > 0 else None,
        currency=info.get("currency") or _fast_info_value(fast, "currency") or "USD",
        week_52_high=week_52_high or 0.0,
        week_52_low=week_52_low or 0.0,
        volume=volume if volume > 0 else 0,
        avg_volume=avg_volume if avg_volume > 0 else 0,
    )


async def get_technicals(ticker: str) -> TechnicalIndicators:
    t = yf.Ticker(ticker.upper())
    hist = _safe_history(t, period="1y", interval="1d")
    return _compute_technicals_from_history(ticker, hist)


async def get_signals(ticker: str) -> SignalsResponse:
    technicals = await get_technicals(ticker)

    bullish = 0
    bearish = 0
    signal_items: List[Signal] = []

    # RSI
    if technicals.rsi is not None:
        rsi_direction = "neutral"
        if technicals.rsi < 30:
            bullish += 1
            rsi_direction = "bullish"
        elif technicals.rsi > 70:
            bearish += 1
            rsi_direction = "bearish"
        signal_items.append(
            Signal(label="RSI", value=str(round(technicals.rsi, 2)), direction=rsi_direction)
        )

    # MACD
    if technicals.macd is not None and technicals.macd_signal is not None:
        macd_direction = "neutral"
        if technicals.macd > technicals.macd_signal:
            bullish += 1
            macd_direction = "bullish"
        elif technicals.macd < technicals.macd_signal:
            bearish += 1
            macd_direction = "bearish"
        signal_items.append(
            Signal(label="MACD", value=str(round(technicals.macd, 4)), direction=macd_direction)
        )

    # Moving averages
    if technicals.price is not None and technicals.sma_50 is not None:
        ma50_direction = "bullish" if technicals.price > technicals.sma_50 else "bearish"
        bullish += 1 if ma50_direction == "bullish" else 0
        bearish += 1 if ma50_direction == "bearish" else 0
        signal_items.append(
            Signal(label="Price vs SMA50", value=str(round(technicals.sma_50, 2)), direction=ma50_direction)
        )

    if technicals.price is not None and technicals.sma_200 is not None:
        ma200_direction = "bullish" if technicals.price > technicals.sma_200 else "bearish"
        bullish += 1 if ma200_direction == "bullish" else 0
        bearish += 1 if ma200_direction == "bearish" else 0
        signal_items.append(
            Signal(label="Price vs SMA200", value=str(round(technicals.sma_200, 2)), direction=ma200_direction)
        )

    # Bollinger position (0–100 scale)
    if technicals.bb_position is not None:
        bb_direction = "neutral"
        if technicals.bb_position < 20:
            bullish += 1
            bb_direction = "bullish"
        elif technicals.bb_position > 80:
            bearish += 1
            bb_direction = "bearish"
        signal_items.append(
            Signal(label="Bollinger Position", value=f"{round(technicals.bb_position, 1)}%", direction=bb_direction)
        )

    # Momentum
    if technicals.momentum_20d is not None:
        mom_direction = "bullish" if technicals.momentum_20d > 0 else "bearish" if technicals.momentum_20d < 0 else "neutral"
        bullish += 1 if mom_direction == "bullish" else 0
        bearish += 1 if mom_direction == "bearish" else 0
        signal_items.append(
            Signal(label="20D Momentum", value=f"{round(technicals.momentum_20d, 2)}%", direction=mom_direction)
        )

    # Trend label
    trend: Optional[str] = None
    price = technicals.price
    sma_50 = technicals.sma_50
    sma_200 = technicals.sma_200
    if sma_200 is not None and sma_50 is not None:
        if price > sma_200 and price > sma_50 and sma_50 > sma_200:
            trend = "STRONG_UPTREND"
        elif price > sma_200:
            trend = "UPTREND"
        elif price < sma_200 and price < sma_50 and sma_50 < sma_200:
            trend = "STRONG_DOWNTREND"
        elif price < sma_200:
            trend = "DOWNTREND"
        else:
            trend = "NEUTRAL"
    elif sma_200 is not None:
        trend = "UPTREND" if price > sma_200 else "DOWNTREND"

    score = bullish - bearish
    overall = "HOLD"
    if score >= 3:
        overall = "BUY"
    elif score <= -3:
        overall = "SELL"

    # Fix 4: include updated_at
    return SignalsResponse(
        ticker=ticker.upper(),
        signal=overall,
        score=float(score),
        trend=trend,
        signals=signal_items,
        updated_at=datetime.utcnow().isoformat() + "Z",
    )


async def get_fundamentals(ticker: str) -> Fundamentals:
    t = yf.Ticker(ticker.upper())
    info = _safe_info(t)

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
        beta=_safe_float(info.get("beta")),
        book_value=_safe_float(info.get("bookValue")),
        price_to_book=_safe_float(info.get("priceToBook")),
        roe=_safe_float(info.get("returnOnEquity")),
    )


# Fix 7: restore get_price_history (used by chart endpoints)
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


# Fix 8: restore compute_history_stats (used by technicals router)
def compute_history_stats(history: list[dict]) -> dict:
    """
    Compute annualised volatility and price momentum from OHLCV history dicts.
    Pure computation — no I/O.
    """
    closes = [row["close"] for row in history if "close" in row]
    result: dict = {"volatility": None, "momentum_5d": None, "momentum_20d": None}
    if len(closes) < 2:
        return result

    returns = [
        math.log(closes[i] / closes[i - 1])
        for i in range(1, len(closes))
        if closes[i - 1] > 0
    ]
    if len(returns) >= 2:
        mean = sum(returns) / len(returns)
        var = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
        result["volatility"] = round(math.sqrt(var) * math.sqrt(252), 4)

    if len(closes) >= 6:
        result["momentum_5d"] = round((closes[-1] / closes[-6] - 1) * 100, 2)
    if len(closes) >= 21:
        result["momentum_20d"] = round((closes[-1] / closes[-21] - 1) * 100, 2)

    return result


async def get_competitors(ticker: str) -> CompetitorsResponse:
    peer_map = {
        "AAPL": ["MSFT", "GOOGL", "AMZN", "NVDA"],
        "MSFT": ["AAPL", "GOOGL", "AMZN", "ORCL"],
        "NVDA": ["AMD", "INTC", "AVGO", "QCOM"],
        "TSLA": ["GM", "F", "RIVN", "NIO"],
        "GOOGL": ["META", "MSFT", "AMZN", "AAPL"],
        "META": ["GOOGL", "SNAP", "PINS", "TWTR"],
        "AMZN": ["MSFT", "GOOGL", "BABA", "SHOP"],
        "JPM": ["BAC", "WFC", "GS", "MS"],
        "BAC": ["JPM", "WFC", "GS", "C"],
        "XOM": ["CVX", "COP", "SLB", "EOG"],
        "JNJ": ["PFE", "ABBV", "MRK", "BMY"],
    }

    # Sector-based fallback for tickers not in the map
    t = yf.Ticker(ticker.upper())
    info = _safe_info(t)
    sector = info.get("sector")

    sector_peers: Dict[str, List[str]] = {
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

    candidates = peer_map.get(ticker.upper()) or [
        p for p in sector_peers.get(sector or "", [])
        if p != ticker.upper()
    ]
    peers = candidates[:5]

    results: List[Competitor] = []
    for p in peers:
        try:
            pt = yf.Ticker(p)
            info_p = _safe_info(pt)
            try:
                fast = getattr(pt, "fast_info", {}) or {}
            except Exception:
                fast = {}

            price = (
                _fast_info_float(fast, "lastPrice")
                or _safe_float(info_p.get("currentPrice"))
                or 0
            )
            prev = (
                _fast_info_float(fast, "previousClose")
                or _safe_float(info_p.get("previousClose"))
                or price
            )
            change_pct = round((price - prev) / prev * 100, 2) if prev and prev != 0 else 0.0
            market_cap = (
                _safe_int(_fast_info_value(fast, "marketCap"))
                or _safe_int(info_p.get("marketCap"))
            ) or None

            results.append(
                Competitor(
                    ticker=p,
                    name=info_p.get("shortName") or info_p.get("longName") or p,
                    price=price,
                    change_pct=change_pct,
                    market_cap=market_cap if market_cap else None,
                    pe_ratio=_safe_float(info_p.get("trailingPE")),
                )
            )
        except Exception:
            continue

    # Fix 6: return CompetitorsResponse directly (router updated to match)
    return CompetitorsResponse(ticker=ticker.upper(), sector=sector, competitors=results)
