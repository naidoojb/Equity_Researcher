import logging
from typing import Callable, TypeVar, Awaitable

from models.schemas import StockOverview, Fundamentals, TechnicalIndicators, SignalsResponse, CompetitorsResponse, Competitor
from services import yfinance_service, alphavantage_service

logger = logging.getLogger(__name__)
T = TypeVar("T")


def _av_enabled() -> bool:
    return alphavantage_service.has_configured_api_key()


async def _run_with_fallback(
    endpoint: str,
    ticker: str,
    primary_fn: Callable[[], Awaitable[T]],
    fallback_fn: Callable[[], Awaitable[T]],
) -> T:
    try:
        result = await primary_fn()
        logger.info(
            "market_data_fetch",
            extra={"endpoint": endpoint, "ticker": ticker.upper(), "provider": "yfinance", "fallback_attempted": False, "fallback_succeeded": False},
        )
        return result
    except Exception as primary_error:
        if not _av_enabled():
            logger.warning(
                "market_data_fetch",
                extra={
                    "endpoint": endpoint,
                    "ticker": ticker.upper(),
                    "provider": "yfinance",
                    "fallback_attempted": False,
                    "fallback_succeeded": False,
                    "reason": "missing_or_invalid_av_key",
                    "error": str(primary_error),
                },
            )
            raise

        logger.info(
            "market_data_fetch",
            extra={"endpoint": endpoint, "ticker": ticker.upper(), "provider": "alphavantage", "fallback_attempted": True, "fallback_succeeded": False},
        )
        try:
            result = await fallback_fn()
            logger.info(
                "market_data_fetch",
                extra={"endpoint": endpoint, "ticker": ticker.upper(), "provider": "alphavantage", "fallback_attempted": True, "fallback_succeeded": True},
            )
            return result
        except Exception as fallback_error:
            logger.exception(
                "market_data_fetch",
                extra={
                    "endpoint": endpoint,
                    "ticker": ticker.upper(),
                    "provider": "alphavantage",
                    "fallback_attempted": True,
                    "fallback_succeeded": False,
                    "primary_error": str(primary_error),
                    "fallback_error": str(fallback_error),
                },
            )
            raise primary_error


async def get_overview_with_fallback(ticker: str) -> StockOverview:
    return await _run_with_fallback(
        endpoint="stock",
        ticker=ticker,
        primary_fn=lambda: yfinance_service.get_overview(ticker),
        fallback_fn=lambda: alphavantage_service.map_stock_overview(ticker),
    )


async def get_fundamentals_with_fallback(ticker: str) -> Fundamentals:
    return await _run_with_fallback(
        endpoint="fundamentals",
        ticker=ticker,
        primary_fn=lambda: yfinance_service.get_fundamentals(ticker),
        fallback_fn=lambda: alphavantage_service.map_fundamentals(ticker),
    )


async def get_technicals_with_fallback(ticker: str) -> TechnicalIndicators:
    async def _fallback_technicals() -> TechnicalIndicators:
        price = 0.0
        try:
            overview = await alphavantage_service.map_stock_overview(ticker)
            price = overview.price
        except Exception:
            pass
        return await alphavantage_service.map_technicals(ticker, price=price)

    return await _run_with_fallback(
        endpoint="technicals",
        ticker=ticker,
        primary_fn=lambda: yfinance_service.get_technicals(ticker),
        fallback_fn=_fallback_technicals,
    )


async def get_signals_with_fallback(ticker: str) -> SignalsResponse:
    technicals = await get_technicals_with_fallback(ticker)
    return yfinance_service.build_signals_response(ticker, technicals)


async def get_competitors_with_fallback(ticker: str) -> CompetitorsResponse:
    # Keep peer discovery from yfinance.
    base = await yfinance_service.get_competitors(ticker)
    if not _av_enabled() or not base.competitors:
        return base

    enriched: list[Competitor] = []
    for comp in base.competitors:
        if comp.price > 0 and comp.pe_ratio is not None and comp.market_cap is not None:
            enriched.append(comp)
            continue

        try:
            av_overview = await alphavantage_service.map_stock_overview(comp.ticker)
            av_fundamentals = await alphavantage_service.map_fundamentals(comp.ticker)
            enriched.append(
                Competitor(
                    ticker=comp.ticker,
                    name=comp.name or av_overview.name,
                    price=comp.price if comp.price > 0 else av_overview.price,
                    change_pct=comp.change_pct if comp.change_pct != 0 else av_overview.change_pct,
                    market_cap=comp.market_cap or av_overview.market_cap,
                    pe_ratio=comp.pe_ratio if comp.pe_ratio is not None else av_fundamentals.pe_ratio,
                )
            )
            logger.info(
                "market_data_fetch",
                extra={"endpoint": "competitors", "ticker": comp.ticker, "provider": "alphavantage", "fallback_attempted": True, "fallback_succeeded": True},
            )
        except Exception:
            enriched.append(comp)
            logger.warning(
                "market_data_fetch",
                extra={"endpoint": "competitors", "ticker": comp.ticker, "provider": "alphavantage", "fallback_attempted": True, "fallback_succeeded": False},
            )

    return CompetitorsResponse(ticker=base.ticker, sector=base.sector, competitors=enriched)
