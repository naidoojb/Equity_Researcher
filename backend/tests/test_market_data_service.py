import os
import unittest
from unittest.mock import AsyncMock, patch

from models.schemas import StockOverview, Fundamentals, TechnicalIndicators, CompetitorsResponse, Competitor
from services import market_data_service, alphavantage_service


class TestMarketDataFallback(unittest.IsolatedAsyncioTestCase):
    async def test_overview_primary_success_no_fallback(self):
        overview = StockOverview(
            ticker="AAPL", name="Apple", price=1, change=0, change_pct=0, volume=1,
            avg_volume=1, market_cap=None, week_52_high=1, week_52_low=1,
            currency="USD", exchange="NASDAQ", sector=None, industry=None,
        )
        with patch("services.yfinance_service.get_overview", AsyncMock(return_value=overview)) as primary, \
             patch("services.alphavantage_service.map_stock_overview", AsyncMock()) as fallback:
            result = await market_data_service.get_overview_with_fallback("AAPL")
            self.assertEqual(result.ticker, "AAPL")
            primary.assert_awaited_once()
            fallback.assert_not_called()

    async def test_overview_primary_error_uses_fallback(self):
        fallback_overview = StockOverview(
            ticker="AAPL", name="Apple", price=2, change=1, change_pct=2, volume=1,
            avg_volume=1, market_cap=10, week_52_high=3, week_52_low=1,
            currency="USD", exchange="NASDAQ", sector="Technology", industry="Consumer Electronics",
        )
        with patch.dict(os.environ, {"ALPHAVANTAGE_KEY": "real_key"}), \
             patch("services.yfinance_service.get_overview", AsyncMock(side_effect=TimeoutError("timeout"))), \
             patch("services.alphavantage_service.map_stock_overview", AsyncMock(return_value=fallback_overview)):
            result = await market_data_service.get_overview_with_fallback("AAPL")
            self.assertEqual(result.price, 2)

    async def test_overview_primary_error_without_key_raises(self):
        with patch.dict(os.environ, {"ALPHAVANTAGE_KEY": ""}), \
             patch("services.yfinance_service.get_overview", AsyncMock(side_effect=RuntimeError("boom"))), \
             patch("services.alphavantage_service.map_stock_overview", AsyncMock()) as fallback:
            with self.assertRaises(RuntimeError):
                await market_data_service.get_overview_with_fallback("AAPL")
            fallback.assert_not_called()

    async def test_signals_uses_technical_fallback_values(self):
        tech = TechnicalIndicators(
            ticker="AAPL", price=100, rsi=20, macd=1.0, macd_signal=0.5, macd_hist=0.5,
            sma_20=90, sma_50=95, sma_200=80, bb_upper=110, bb_lower=90, bb_middle=100,
            ema_20=99, bb_position=10, volatility=None, momentum_5d=None, momentum_20d=2.0, signals=[]
        )
        with patch("services.market_data_service.get_technicals_with_fallback", AsyncMock(return_value=tech)):
            result = await market_data_service.get_signals_with_fallback("AAPL")
            self.assertEqual(result.signal, "BUY")
            self.assertGreaterEqual(len(result.signals), 3)

    async def test_competitors_enrichment_partial(self):
        comp_resp = CompetitorsResponse(
            ticker="AAPL",
            sector="Technology",
            competitors=[
                Competitor(ticker="MSFT", name="Microsoft", price=0, change_pct=0, market_cap=None, pe_ratio=None)
            ],
        )
        av_overview = StockOverview(
            ticker="MSFT", name="Microsoft", price=300, change=1, change_pct=0.33, volume=1,
            avg_volume=1, market_cap=100, week_52_high=350, week_52_low=200,
            currency="USD", exchange="NASDAQ", sector="Technology", industry="Software",
        )
        av_fund = Fundamentals(
            ticker="MSFT", pe_ratio=30, forward_pe=None, eps=None, revenue=None,
            revenue_growth=None, gross_margin=None, operating_margin=None, net_margin=None,
            debt_to_equity=None, current_ratio=None, dividend_yield=None,
            book_value=None, price_to_book=None, beta=None, roe=None,
        )
        with patch.dict(os.environ, {"ALPHAVANTAGE_KEY": "real_key"}), \
             patch("services.yfinance_service.get_competitors", AsyncMock(return_value=comp_resp)), \
             patch("services.alphavantage_service.map_stock_overview", AsyncMock(return_value=av_overview)), \
             patch("services.alphavantage_service.map_fundamentals", AsyncMock(return_value=av_fund)):
            result = await market_data_service.get_competitors_with_fallback("AAPL")
            self.assertEqual(result.competitors[0].price, 300)
            self.assertEqual(result.competitors[0].pe_ratio, 30)


class TestAlphaVantageMappings(unittest.IsolatedAsyncioTestCase):
    async def test_partial_fundamentals_mapping_nullable_fields(self):
        with patch("services.alphavantage_service.get_company_overview", AsyncMock(return_value={"PERatio": "20", "EPS": "2"})), \
             patch("services.alphavantage_service.get_income_statement", AsyncMock(return_value={"annualReports": [{}]})), \
             patch("services.alphavantage_service.get_balance_sheet", AsyncMock(return_value={"annualReports": [{}]})):
            result = await alphavantage_service.map_fundamentals("AAPL")
            self.assertEqual(result.pe_ratio, 20)
            self.assertIsNone(result.revenue)
            self.assertIsNone(result.current_ratio)


if __name__ == "__main__":
    unittest.main()
