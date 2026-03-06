import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException
from models.schemas import SignalsResponse, Signal
from services import yfinance_service, alphavantage_service, newsapi_service
from utils.cache import cache_signals
import anthropic

router = APIRouter()
_client = anthropic.Anthropic()


@router.get("/{ticker}/signals", response_model=SignalsResponse)
async def get_signals(ticker: str):
    """Get aggregated daily bull/bear signals with composite score."""
    try:
        return await _cached_signals(ticker.upper())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@cache_signals
async def _cached_signals(ticker: str) -> SignalsResponse:
    overview, rsi, (macd, macd_sig, macd_hist), sma_50, sma_200, raw_news = await asyncio.gather(
        yfinance_service.get_overview(ticker),
        alphavantage_service.get_rsi(ticker),
        alphavantage_service.get_macd(ticker),
        alphavantage_service.get_sma(ticker, 50),
        alphavantage_service.get_sma(ticker, 200),
        newsapi_service.get_news(ticker, limit=10),
    )

    signals: list[Signal] = []
    score_components: list[float] = []
    price = overview.price

    # --- Momentum signals ---
    if overview.change_pct > 2:
        signals.append(Signal(label="Daily Momentum", value=f"+{overview.change_pct:.2f}%", direction="bullish"))
        score_components.append(0.3)
    elif overview.change_pct < -2:
        signals.append(Signal(label="Daily Momentum", value=f"{overview.change_pct:.2f}%", direction="bearish"))
        score_components.append(-0.3)
    else:
        signals.append(Signal(label="Daily Momentum", value=f"{overview.change_pct:.2f}%", direction="neutral"))
        score_components.append(overview.change_pct / 10)

    # --- Volume signal ---
    if overview.avg_volume > 0:
        vol_ratio = overview.volume / overview.avg_volume
        if vol_ratio > 1.5:
            signals.append(Signal(label="Volume Surge", value=f"{vol_ratio:.1f}x avg", direction="bullish"))
            score_components.append(0.15)
        elif vol_ratio < 0.5:
            signals.append(Signal(label="Low Volume", value=f"{vol_ratio:.1f}x avg", direction="bearish"))
            score_components.append(-0.1)

    # --- RSI signal ---
    if rsi is not None:
        if rsi < 30:
            signals.append(Signal(label="RSI Oversold", value=f"{rsi:.1f}", direction="bullish"))
            score_components.append(0.4)
        elif rsi > 70:
            signals.append(Signal(label="RSI Overbought", value=f"{rsi:.1f}", direction="bearish"))
            score_components.append(-0.4)
        else:
            score_components.append((50 - rsi) / 100)

    # --- MACD signal ---
    if macd_hist is not None:
        if macd_hist > 0:
            signals.append(Signal(label="MACD Bullish", value=f"{macd_hist:.4f}", direction="bullish"))
            score_components.append(0.25)
        else:
            signals.append(Signal(label="MACD Bearish", value=f"{macd_hist:.4f}", direction="bearish"))
            score_components.append(-0.25)

    # --- Trend signals ---
    if sma_200 is not None:
        if price > sma_200:
            signals.append(Signal(label="Above 200-day MA", value=f"${sma_200:.2f}", direction="bullish"))
            score_components.append(0.2)
        else:
            signals.append(Signal(label="Below 200-day MA", value=f"${sma_200:.2f}", direction="bearish"))
            score_components.append(-0.2)

    # --- News sentiment ---
    news_scores = await _batch_sentiment_score(raw_news)
    if news_scores:
        avg_news = sum(news_scores) / len(news_scores)
        direction = "bullish" if avg_news > 0.1 else "bearish" if avg_news < -0.1 else "neutral"
        signals.append(Signal(label="News Sentiment", value=f"{avg_news:+.2f}", direction=direction))
        score_components.append(avg_news * 0.3)

    # --- Composite score ---
    composite = max(-1.0, min(1.0, sum(score_components) / max(len(score_components), 1)))

    if composite >= 0.5:
        signal_label = "STRONG BUY"
    elif composite >= 0.15:
        signal_label = "BUY"
    elif composite <= -0.5:
        signal_label = "STRONG SELL"
    elif composite <= -0.15:
        signal_label = "SELL"
    else:
        signal_label = "HOLD"

    return SignalsResponse(
        ticker=ticker,
        signal=signal_label,
        score=round(composite, 3),
        signals=signals,
        updated_at=datetime.utcnow().isoformat() + "Z",
    )


async def _batch_sentiment_score(articles: list[dict]) -> list[float]:
    """Score news sentiment using Claude Haiku (fast, cheap)."""
    if not articles:
        return []

    titles = [a.get("title", "") for a in articles if a.get("title") and a.get("title") != "[Removed]"]
    if not titles:
        return []

    titles_str = "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles[:10]))
    try:
        response = _client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": (
                    "Score each headline's sentiment from -1.0 (bearish) to 1.0 (bullish). "
                    "Reply with ONLY a comma-separated list of numbers in order.\n\n"
                    f"Headlines:\n{titles_str}"
                ),
            }],
        )
        raw = response.content[0].text.strip()
        scores = [max(-1.0, min(1.0, float(s.strip()))) for s in raw.split(",")]
        return scores
    except Exception:
        return []
