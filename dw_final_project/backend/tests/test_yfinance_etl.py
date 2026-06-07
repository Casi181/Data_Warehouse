"""Tests for the yfinance ETL pipeline.

Covers: YFinanceClient, Transformer with yfinance data, Extractor dispatch,
and IngestionService end-to-end with mocked dependencies.
"""

import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import date, datetime, UTC
import asyncio

import pandas as pd
from etl.extractor import RawPage, Extractor
from etl.transformer import Transformer
from etl.providers.yfinance_client import YFinanceClient, YFINANCE_COLUMNS
from schemas.ingestion_schemas import IngestionRequest, IngestionResult
from services.ingestion_service import IngestionService
from models.time_series_model import TimeSeriesRecord


def _run(coro):
    """Helper to run an async coroutine in tests."""
    return asyncio.run(coro)


def _make_sample_df(rows=5, start_date="2024-01-02"):
    """Build a pandas DataFrame that mimics yfinance output."""
    dates = pd.bdate_range(start=start_date, periods=rows)
    data = {
        "Open": [100.0 + i for i in range(rows)],
        "High": [105.0 + i for i in range(rows)],
        "Low": [95.0 + i for i in range(rows)],
        "Close": [102.0 + i for i in range(rows)],
        "Volume": [1_000_000 + i * 10_000 for i in range(rows)],
    }
    return pd.DataFrame(data, index=dates)


# ──────────────────────────────────────────────────────────────────────
# YFinanceClient
# ──────────────────────────────────────────────────────────────────────


class TestYFinanceClient(unittest.TestCase):
    """Unit tests for YFinanceClient (yfinance is mocked)."""

    @patch("etl.providers.yfinance_client.yf")
    def test_fetch_returns_records(self, mock_yf):
        """Valid ticker returns RawPage with correct records."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = _make_sample_df(3)
        mock_yf.Ticker.return_value = mock_ticker

        client = YFinanceClient()
        page = _run(client.fetch_dataset("AAPL", period="1mo"))

        self.assertIsInstance(page, RawPage)
        self.assertEqual(page.record_count, 3)
        self.assertEqual(len(page.records), 3)
        self.assertIsNone(page.next_cursor)
        self.assertEqual(page.columns, YFINANCE_COLUMNS)

        # Verify record structure
        rec = page.records[0]
        self.assertIn("Date", rec)
        self.assertIn("Open", rec)
        self.assertIn("High", rec)
        self.assertIn("Low", rec)
        self.assertIn("Close", rec)
        self.assertIn("Volume", rec)
        self.assertIsInstance(rec["Open"], float)
        self.assertIsInstance(rec["Volume"], int)

    @patch("etl.providers.yfinance_client.yf")
    def test_fetch_empty_dataframe(self, mock_yf):
        """Empty DataFrame returns empty RawPage."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()
        mock_yf.Ticker.return_value = mock_ticker

        client = YFinanceClient()
        page = _run(client.fetch_dataset("INVALID", period="1y"))

        self.assertEqual(page.record_count, 0)
        self.assertEqual(page.records, [])

    @patch("etl.providers.yfinance_client.yf")
    def test_fetch_none_on_error(self, mock_yf):
        """Exception in yfinance returns empty RawPage."""
        mock_ticker = MagicMock()
        mock_ticker.history.side_effect = Exception("Network error")
        mock_yf.Ticker.return_value = mock_ticker

        client = YFinanceClient()
        page = _run(client.fetch_dataset("AAPL"))

        self.assertEqual(page.record_count, 0)
        self.assertEqual(page.records, [])

    @patch("etl.providers.yfinance_client.yf")
    def test_fetch_passes_period(self, mock_yf):
        """The requested period is forwarded to yfinance."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = _make_sample_df(1)
        mock_yf.Ticker.return_value = mock_ticker

        client = YFinanceClient()
        _run(client.fetch_dataset("MSFT", period="5y"))

        mock_ticker.history.assert_called_once_with(
            period="5y", interval="1d", auto_adjust=True
        )

    @patch("etl.providers.yfinance_client.yf")
    def test_fetch_uppercase_ticker(self, mock_yf):
        """Ticker is uppercased automatically."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = _make_sample_df(1)
        mock_yf.Ticker.return_value = mock_ticker

        client = YFinanceClient()
        _run(client.fetch_dataset("aapl"))

        mock_yf.Ticker.assert_called_with("AAPL")

    @patch("etl.providers.yfinance_client.yf")
    def test_date_format_iso(self, mock_yf):
        """Dates are formatted as YYYY-MM-DD strings."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = _make_sample_df(1, start_date="2024-06-15")
        mock_yf.Ticker.return_value = mock_ticker

        client = YFinanceClient()
        page = _run(client.fetch_dataset("AAPL"))

        self.assertRegex(page.records[0]["Date"], r"^\d{4}-\d{2}-\d{2}$")


# ──────────────────────────────────────────────────────────────────────
# Transformer with yfinance-shaped data
# ──────────────────────────────────────────────────────────────────────


class TestTransformerWithYFinanceData(unittest.TestCase):
    """Tests that Transformer correctly processes yfinance-style records."""

    def setUp(self):
        self.transformer = Transformer()

    def test_transform_ohlcv_records(self):
        """Standard OHLCV records are transformed into TimeSeriesRecords."""
        raw = [
            {"Date": "2024-03-01", "Open": 150.0, "High": 155.0,
             "Low": 148.0, "Close": 153.0, "Volume": 5000000},
            {"Date": "2024-03-04", "Open": 153.0, "High": 158.0,
             "Low": 152.0, "Close": 157.0, "Volume": 4500000},
        ]
        columns = YFINANCE_COLUMNS

        results = self.transformer.transform(raw, columns, "AAPL", "YFINANCE")

        self.assertEqual(len(results), 2)
        rec = results[0]
        self.assertIsInstance(rec, TimeSeriesRecord)
        self.assertEqual(rec.asset_id, "YFINANCE/AAPL")
        self.assertEqual(rec.data_source_id, "YFINANCE")
        self.assertEqual(rec.business_date, date(2024, 3, 1))
        self.assertEqual(rec.business_date_year, 2024)
        self.assertAlmostEqual(rec.values_double["Open"], 150.0)
        self.assertAlmostEqual(rec.values_double["Close"], 153.0)
        # Volume is numeric and should be parsed as float in values_double
        self.assertIn("Volume", rec.values_double)

    def test_transform_empty_input(self):
        """Empty input produces empty output."""
        results = self.transformer.transform([], YFINANCE_COLUMNS, "AAPL", "YFINANCE")
        self.assertEqual(results, [])

    def test_transform_skips_bad_date(self):
        """Records with invalid dates are silently skipped."""
        raw = [
            {"Date": "not-a-date", "Open": 100.0, "Close": 101.0},
        ]
        results = self.transformer.transform(raw, ["Date", "Open", "Close"], "X", "YFINANCE")
        self.assertEqual(len(results), 0)

    def test_transform_skips_missing_date(self):
        """Records missing the Date field are skipped."""
        raw = [{"Open": 100.0, "Close": 101.0}]
        results = self.transformer.transform(raw, ["Date", "Open", "Close"], "X", "YFINANCE")
        self.assertEqual(len(results), 0)

    def test_transform_handles_mixed_types(self):
        """Non-numeric values go into values_text, numeric into values_double."""
        raw = [
            {"Date": "2024-01-02", "Open": 100.0, "Notes": "ex-dividend"},
        ]
        columns = ["Date", "Open", "Notes"]
        results = self.transformer.transform(raw, columns, "AAPL", "YFINANCE")

        self.assertEqual(len(results), 1)
        self.assertAlmostEqual(results[0].values_double["Open"], 100.0)
        self.assertEqual(results[0].values_text["Notes"], "ex-dividend")


# ──────────────────────────────────────────────────────────────────────
# Extractor dispatch
# ──────────────────────────────────────────────────────────────────────


class TestExtractorDispatch(unittest.TestCase):
    """Tests that Extractor correctly routes to the right provider."""

    @patch("etl.providers.yfinance_client.yf")
    @patch("etl.providers.nasdaq_client.get_settings")
    def test_yfinance_provider_registered(self, _mock_settings, mock_yf):
        """YFINANCE provider is available and dispatches correctly."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = _make_sample_df(2)
        mock_yf.Ticker.return_value = mock_ticker

        extractor = Extractor()
        page = _run(extractor.fetch("YFINANCE", "AAPL", period="1mo"))

        self.assertEqual(page.record_count, 2)
        self.assertIsNone(page.next_cursor)

    @patch("etl.providers.yfinance_client.yf")
    @patch("etl.providers.nasdaq_client.get_settings")
    def test_unknown_provider_raises(self, _mock_settings, _mock_yf):
        """Unknown provider name raises ValueError."""
        extractor = Extractor()
        with self.assertRaises(ValueError) as ctx:
            _run(extractor.fetch("UNKNOWN", "AAPL"))
        self.assertIn("Unknown provider", str(ctx.exception))

    @patch("etl.providers.yfinance_client.yf")
    @patch("etl.providers.nasdaq_client.get_settings")
    def test_all_providers_registered(self, _mock_settings, _mock_yf):
        """Extractor has YFINANCE, NASDAQ-DATA-LINK, and BITFINEX registered."""
        extractor = Extractor()
        self.assertIn("YFINANCE", extractor._clients)
        self.assertIn("NASDAQ-DATA-LINK", extractor._clients)
        self.assertIn("BITFINEX", extractor._clients)


# ──────────────────────────────────────────────────────────────────────
# IngestionService (end-to-end with mocks)
# ──────────────────────────────────────────────────────────────────────


class TestIngestionServiceWithYFinance(unittest.TestCase):
    """Tests IngestionService with mocked extractor/transformer/loader."""

    def setUp(self):
        self.mock_extractor = MagicMock()
        self.mock_transformer = MagicMock()
        self.mock_loader = MagicMock()
        self.service = IngestionService(
            self.mock_extractor, self.mock_transformer, self.mock_loader
        )

    def test_single_ticker_ingestion(self):
        """Ingesting one ticker calls extract -> transform -> load correctly."""
        fake_page = RawPage(
            records=[
                {"Date": "2024-03-01", "Open": 150.0, "Close": 153.0},
            ],
            columns=YFINANCE_COLUMNS,
            next_cursor=None,
            record_count=1,
        )
        self.mock_extractor.fetch = AsyncMock(return_value=fake_page)

        fake_record = TimeSeriesRecord(
            asset_id="YFINANCE/AAPL", data_source_id="YFINANCE",
            business_date_year=2024, business_date=date(2024, 3, 1),
            system_date=datetime.now(UTC),
            values_double={"Open": 150.0, "Close": 153.0},
        )
        self.mock_transformer.transform.return_value = [fake_record]
        self.mock_loader.load.return_value = 1

        request = IngestionRequest(
            provider="YFINANCE", dataset_codes=["AAPL"], period="1mo"
        )
        result = _run(self.service.run_ingestion(request))

        self.assertIsInstance(result, IngestionResult)
        self.assertEqual(result.fetched, 1)
        self.assertEqual(result.stored, 1)
        self.assertEqual(result.errors, 0)

        # Verify extractor was called with period
        self.mock_extractor.fetch.assert_called_once_with(
            provider="YFINANCE",
            dataset_code="AAPL",
            cursor=None,
            period="1mo",
        )

    def test_multiple_tickers(self):
        """Ingesting multiple tickers processes each one."""
        fake_page = RawPage(
            records=[{"Date": "2024-01-02", "Open": 100.0}],
            columns=YFINANCE_COLUMNS,
            next_cursor=None,
            record_count=1,
        )
        self.mock_extractor.fetch = AsyncMock(return_value=fake_page)
        self.mock_transformer.transform.return_value = [MagicMock()]
        self.mock_loader.load.return_value = 1

        request = IngestionRequest(
            provider="YFINANCE",
            dataset_codes=["AAPL", "MSFT", "GOOGL"],
        )
        result = _run(self.service.run_ingestion(request))

        self.assertEqual(result.fetched, 3)
        self.assertEqual(result.stored, 3)
        self.assertEqual(self.mock_extractor.fetch.call_count, 3)

    def test_empty_dataset(self):
        """An empty RawPage from yfinance yields zero records stored."""
        fake_page = RawPage(
            records=[], columns=YFINANCE_COLUMNS,
            next_cursor=None, record_count=0,
        )
        self.mock_extractor.fetch = AsyncMock(return_value=fake_page)
        self.mock_transformer.transform.return_value = []
        self.mock_loader.load.return_value = 0

        request = IngestionRequest(
            provider="YFINANCE", dataset_codes=["INVALID"]
        )
        result = _run(self.service.run_ingestion(request))

        self.assertEqual(result.fetched, 0)
        self.assertEqual(result.stored, 0)

    def test_transform_errors_counted(self):
        """Transformation failures are counted as errors."""
        fake_page = RawPage(
            records=[{"Date": "2024-01-02"}, {"Date": "bad"}],
            columns=YFINANCE_COLUMNS,
            next_cursor=None,
            record_count=2,
        )
        self.mock_extractor.fetch = AsyncMock(return_value=fake_page)
        # Only one record survives transformation
        self.mock_transformer.transform.return_value = [MagicMock()]
        self.mock_loader.load.return_value = 1

        request = IngestionRequest(
            provider="YFINANCE", dataset_codes=["AAPL"]
        )
        result = _run(self.service.run_ingestion(request))

        self.assertEqual(result.fetched, 2)
        self.assertEqual(result.stored, 1)
        self.assertEqual(result.errors, 1)


# ──────────────────────────────────────────────────────────────────────
# IngestionRequest / IngestionResult schemas
# ──────────────────────────────────────────────────────────────────────


class TestIngestionSchemas(unittest.TestCase):
    """Schema validation for updated ingestion DTOs."""

    def test_default_provider_is_yfinance(self):
        req = IngestionRequest(dataset_codes=["AAPL"])
        self.assertEqual(req.provider, "YFINANCE")

    def test_default_period_is_1y(self):
        req = IngestionRequest(dataset_codes=["AAPL"])
        self.assertEqual(req.period, "1y")

    def test_custom_period(self):
        req = IngestionRequest(dataset_codes=["AAPL"], period="max")
        self.assertEqual(req.period, "max")

    def test_multiple_dataset_codes(self):
        req = IngestionRequest(dataset_codes=["AAPL", "MSFT", "BTC-USD"])
        self.assertEqual(len(req.dataset_codes), 3)

    def test_ingestion_result_defaults(self):
        result = IngestionResult()
        self.assertEqual(result.fetched, 0)
        self.assertEqual(result.stored, 0)
        self.assertEqual(result.skipped, 0)
        self.assertEqual(result.errors, 0)


if __name__ == "__main__":
    unittest.main()
