from pydantic import BaseModel
from typing import Optional


class StockOverview(BaseModel):
    ticker: str
    name: str
    price: float
    change: float
    change_pct: float
    volume: int
    avg_volume: int
    market_cap: Optional[float]
    week_52_high: float
    week_52_low: float
    currency: str
    exchange: str
    sector: Optional[str]
    industry: Optional[str]
    previous_close: Optional[float] = None


class Signal(BaseModel):
    label: str
    value: str
    direction: str  # "bullish" | "bearish" | "neutral"


class SignalsResponse(BaseModel):
    ticker: str
    signal: str          # "STRONG BUY" | "BUY" | "HOLD" | "SELL" | "STRONG SELL"
    score: float         # -1.0 to 1.0
    trend: Optional[str] = None  # STRONG_UPTREND | UPTREND | NEUTRAL | DOWNTREND | STRONG_DOWNTREND
    signals: list[Signal]
    updated_at: str


class NewsItem(BaseModel):
    title: str
    source: str
    url: str
    published_at: str
    sentiment: float     # -1.0 to 1.0
    sentiment_label: str # "Positive" | "Negative" | "Neutral"
    summary: Optional[str]


class NewsResponse(BaseModel):
    ticker: str
    articles: list[NewsItem]
    avg_sentiment: float


class TechnicalIndicators(BaseModel):
    ticker: str
    rsi: Optional[float]
    macd: Optional[float]
    macd_signal: Optional[float]
    macd_hist: Optional[float]
    sma_20: Optional[float]
    sma_50: Optional[float]
    sma_200: Optional[float]
    bb_upper: Optional[float]
    bb_lower: Optional[float]
    bb_middle: Optional[float]
    ema_20: Optional[float] = None
    bb_position: Optional[float] = None   # 0–100 (0 = at lower band, 100 = at upper band)
    volatility: Optional[float] = None    # annualised, e.g. 0.28 = 28%
    momentum_5d: Optional[float] = None   # % price change over 5 trading days
    momentum_20d: Optional[float] = None  # % price change over 20 trading days
    price: float
    signals: list[Signal]


class Fundamentals(BaseModel):
    ticker: str
    pe_ratio: Optional[float]
    forward_pe: Optional[float]
    eps: Optional[float]
    revenue: Optional[float]
    revenue_growth: Optional[float]
    gross_margin: Optional[float]
    operating_margin: Optional[float]
    net_margin: Optional[float]
    debt_to_equity: Optional[float]
    current_ratio: Optional[float]
    dividend_yield: Optional[float]
    book_value: Optional[float]
    price_to_book: Optional[float]
    beta: Optional[float]
    roe: Optional[float] = None  # return on equity as decimal, e.g. 0.32 = 32%


class Competitor(BaseModel):
    ticker: str
    name: str
    price: float
    change_pct: float
    market_cap: Optional[float]
    pe_ratio: Optional[float]


class CompetitorsResponse(BaseModel):
    ticker: str
    sector: Optional[str]
    competitors: list[Competitor]


class SearchResult(BaseModel):
    ticker: str
    name: str
    exchange: str
    sector: Optional[str]
