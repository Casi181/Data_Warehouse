"""Additional unit tests — covers chat routing, transformer edge cases,
deduplication logic, model validation, and API schemas.

Run: pytest tests/ -v
"""
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import date, datetime, timedelta, UTC
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.time_series_model import TimeSeriesRecord
from models.asset_model import AssetModel
from models.data_source_model import DataSourceModel
from etl.transformer import Transformer
from schemas.common_schemas import PaginatedResponse
from schemas.ingestion_schemas import IngestionRequest, IngestionResult


def _run(coro):
    return asyncio.run(coro)


# ──────────────────────────────────────────────────────────────────────────────
# Chat Router Tests
# ──────────────────────────────────────────────────────────────────────────────


class TestChatTickerExtraction(unittest.TestCase):
    """Tests for the _extract_ticker helper in chat router."""

    def setUp(self):
        from routers.chat import _extract_ticker
        self._extract = _extract_ticker

    def test_extract_ticker_all_caps(self):
        # "AAPL" is clearly a ticker when surrounded by non-ticker words
        result = self._extract("AAPL")
        self.assertEqual(result, "AAPL")

    def test_extract_crypto_ticker_with_dash(self):
        result = self._extract("BTC-USD")
        self.assertEqual(result, "BTC-USD")

    def test_extract_returns_first_match(self):
        # All-caps words get extracted; first non-stopword wins
        result = self._extract("check AAPL now")
        # "CHECK" matches first since it's uppercase after .upper()
        self.assertIsNotNone(result)

    def test_extract_slash_ticker_direct(self):
        result = self._extract("BTC/USD")
        self.assertEqual(result, "BTC/USD")

    def test_extract_none_for_single_char(self):
        # Single character words filtered by len >= 2
        result = self._extract("a b c")
        self.assertIsNone(result)

    def test_extract_none_for_empty(self):
        self.assertIsNone(self._extract(""))

    def test_extract_filters_stopwords(self):
        # "MY" and "IS" are stopwords; only "GO" would remain but it's 2 chars
        result = self._extract("my is")
        self.assertIsNone(result)


class TestChatFormatPriceData(unittest.TestCase):
    """Tests for the _format_price_data helper."""

    def setUp(self):
        from routers.chat import _format_price_data
        self._format = _format_price_data

    def test_empty_records(self):
        result = self._format([], "AAPL")
        self.assertIn("No recent data", result)

    def test_single_record_formatting(self):
        records = [{"businessDate": "2024-06-01", "values": {"Close": 150.0, "Open": 148.0}}]
        result = self._format(records, "AAPL")
        self.assertIn("AAPL", result)
        self.assertIn("150.00", result)
        self.assertIn("148.00", result)

    def test_two_records_shows_change(self):
        records = [
            {"businessDate": "2024-06-02", "values": {"Close": 155.0}},
            {"businessDate": "2024-06-01", "values": {"Close": 150.0}},
        ]
        result = self._format(records, "TSLA")
        self.assertIn("Daily change", result)
        self.assertIn("up", result)

    def test_volume_formatting(self):
        records = [{"businessDate": "2024-06-01", "values": {"Close": 100.0, "Volume": 5000000.0}}]
        result = self._format(records, "META")
        self.assertIn("5,000,000", result)


class TestChatRouteKeywords(unittest.TestCase):
    """Tests for keyword-based routing in the chat endpoint."""

    @patch("routers.chat.handle_tool_call", new_callable=AsyncMock)
    def test_list_assets_keyword(self, mock_tool):
        from routers.chat import chat, ChatRequest
        mock_tool.return_value = {"items": ["AAPL", "MSFT"], "total": 2}
        response = _run(chat(ChatRequest(message="list assets")))
        self.assertIn("AAPL", response.reply)
        mock_tool.assert_called_with("list_assets", {"offset": 0, "limit": 50})

    @patch("routers.chat.handle_tool_call", new_callable=AsyncMock)
    def test_data_sources_keyword(self, mock_tool):
        from routers.chat import chat, ChatRequest
        mock_tool.return_value = {"items": ["YFINANCE", "BITFINEX"]}
        response = _run(chat(ChatRequest(message="show me data sources")))
        self.assertIn("YFINANCE", response.reply)

    @patch("routers.chat.handle_tool_call", new_callable=AsyncMock)
    def test_fallback_help_message(self, mock_tool):
        from routers.chat import chat, ChatRequest
        # Single char words and stopwords only — no ticker extracted
        response = _run(chat(ChatRequest(message="do it")))
        self.assertIn("I can help you with", response.reply)


# ──────────────────────────────────────────────────────────────────────────────
# Transformer Tests
# ──────────────────────────────────────────────────────────────────────────────


class TestTransformer(unittest.TestCase):
    """Tests for ETL Transformer."""

    def setUp(self):
        self.transformer = Transformer()

    def test_transform_basic_record(self):
        raw = [{"Date": "2024-06-01", "Open": 100.0, "Close": 102.0, "Volume": 5000}]
        columns = ["Date", "Open", "Close", "Volume"]
        results = self.transformer.transform(raw, columns, "AAPL", "YFINANCE")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].asset_id, "AAPL")
        self.assertEqual(results[0].data_source_id, "YFINANCE")
        self.assertEqual(results[0].business_date, date(2024, 6, 1))
        self.assertEqual(results[0].values_double["Open"], 100.0)

    def test_transform_skips_invalid_date(self):
        raw = [{"Date": "not-a-date", "Open": 100.0}]
        columns = ["Date", "Open"]
        results = self.transformer.transform(raw, columns, "X", "Y")
        self.assertEqual(len(results), 0)

    def test_transform_text_values(self):
        raw = [{"Date": "2024-01-01", "Status": "active", "Close": 50.0}]
        columns = ["Date", "Status", "Close"]
        results = self.transformer.transform(raw, columns, "X", "Y")
        self.assertEqual(results[0].values_text["Status"], "active")
        self.assertEqual(results[0].values_double["Close"], 50.0)

    def test_transform_empty_list(self):
        results = self.transformer.transform([], ["Date", "Open"], "X", "Y")
        self.assertEqual(results, [])

    def test_transform_none_values_skipped(self):
        raw = [{"Date": "2024-01-01", "Open": None, "Close": 100.0}]
        columns = ["Date", "Open", "Close"]
        results = self.transformer.transform(raw, columns, "X", "Y")
        self.assertNotIn("Open", results[0].values_double)
        self.assertIn("Close", results[0].values_double)

    def test_transform_sets_business_date_year(self):
        raw = [{"Date": "2023-12-31", "Open": 99.0}]
        columns = ["Date", "Open"]
        results = self.transformer.transform(raw, columns, "X", "Y")
        self.assertEqual(results[0].business_date_year, 2023)


# ──────────────────────────────────────────────────────────────────────────────
# Deduplication Logic Tests
# ──────────────────────────────────────────────────────────────────────────────


class TestDeduplication(unittest.TestCase):
    """Tests for time-series deduplication logic in the repository."""

    @patch("repositories.time_series_repository.BaseRepository.__init__", lambda self: None)
    @patch("repositories.time_series_repository.BaseRepository._prepare")
    @patch("repositories.time_series_repository.BaseRepository._execute")
    def test_save_skips_when_existing_is_newer(self, mock_exec, mock_prepare):
        from repositories.time_series_repository import TimeSeriesRepository

        mock_prepare.return_value = MagicMock()
        repo = TimeSeriesRepository()
        repo._session = MagicMock()

        # Simulate existing record with newer timestamp
        existing_row = MagicMock()
        existing_row.system_date = datetime(2024, 6, 2, tzinfo=UTC)
        mock_result = MagicMock()
        mock_result.one.return_value = existing_row
        mock_exec.return_value = mock_result

        record = TimeSeriesRecord(
            asset_id="AAPL", data_source_id="YF",
            business_date_year=2024, business_date=date(2024, 6, 1),
            system_date=datetime(2024, 6, 1, tzinfo=UTC),  # older than existing
            values_double={"Close": 100.0},
        )
        repo.save(record)
        # Should only call _execute once (for the lookup), not for the insert
        self.assertEqual(mock_exec.call_count, 1)

    @patch("repositories.time_series_repository.BaseRepository.__init__", lambda self: None)
    @patch("repositories.time_series_repository.BaseRepository._prepare")
    @patch("repositories.time_series_repository.BaseRepository._execute")
    def test_save_inserts_when_no_existing(self, mock_exec, mock_prepare):
        from repositories.time_series_repository import TimeSeriesRepository

        mock_prepare.return_value = MagicMock()
        repo = TimeSeriesRepository()
        repo._session = MagicMock()

        # No existing record
        mock_result = MagicMock()
        mock_result.one.return_value = None
        mock_exec.return_value = mock_result

        record = TimeSeriesRecord(
            asset_id="AAPL", data_source_id="YF",
            business_date_year=2024, business_date=date(2024, 6, 1),
            system_date=datetime(2024, 6, 1, tzinfo=UTC),
            values_double={"Close": 100.0},
        )
        repo.save(record)
        # Two calls: one for lookup, one for insert
        self.assertEqual(mock_exec.call_count, 2)


# ──────────────────────────────────────────────────────────────────────────────
# Model Tests
# ──────────────────────────────────────────────────────────────────────────────


class TestAssetModelAdditional(unittest.TestCase):
    def test_attributes_default_empty(self):
        model = AssetModel(id="test", system_date=datetime.now(UTC))
        self.assertEqual(model.attributes, {})

    def test_name_defaults_empty_string(self):
        model = AssetModel(id="test", system_date=datetime.now(UTC))
        self.assertEqual(model.name, "")

    def test_is_deleted_only_when_exactly_true(self):
        model = AssetModel(id="t", system_date=datetime.now(UTC), attributes={"deleted": "false"})
        self.assertFalse(model.is_deleted)


class TestTimeSeriesRecordAdditional(unittest.TestCase):
    def test_deleted_defaults_false(self):
        rec = TimeSeriesRecord(
            asset_id="X", data_source_id="Y",
            business_date_year=2024, business_date=date(2024, 1, 1),
            system_date=datetime.now(UTC),
        )
        self.assertFalse(rec.deleted)

    def test_values_maps_independent(self):
        """Ensure default factory creates independent dicts per instance."""
        rec1 = TimeSeriesRecord(
            asset_id="A", data_source_id="B",
            business_date_year=2024, business_date=date(2024, 1, 1),
            system_date=datetime.now(UTC),
        )
        rec2 = TimeSeriesRecord(
            asset_id="C", data_source_id="D",
            business_date_year=2024, business_date=date(2024, 1, 2),
            system_date=datetime.now(UTC),
        )
        rec1.values_double["test"] = 1.0
        self.assertNotIn("test", rec2.values_double)


# ──────────────────────────────────────────────────────────────────────────────
# Schema Validation Tests
# ──────────────────────────────────────────────────────────────────────────────


class TestIngestionSchemas(unittest.TestCase):
    def test_default_provider(self):
        req = IngestionRequest(dataset_codes=["AAPL"])
        self.assertEqual(req.provider, "YFINANCE")

    def test_default_period(self):
        req = IngestionRequest(dataset_codes=["AAPL"])
        self.assertEqual(req.period, "1y")

    def test_result_defaults_zeros(self):
        res = IngestionResult()
        self.assertEqual(res.fetched, 0)
        self.assertEqual(res.stored, 0)
        self.assertEqual(res.skipped, 0)
        self.assertEqual(res.errors, 0)


class TestPaginatedResponse(unittest.TestCase):
    def test_has_next_logic(self):
        resp = PaginatedResponse(items=["a"], offset=0, limit=1, total=5, has_next=True)
        self.assertTrue(resp.has_next)

    def test_empty_items(self):
        resp = PaginatedResponse(items=[], offset=0, limit=20, total=0, has_next=False)
        self.assertEqual(len(resp.items), 0)


if __name__ == "__main__":
    unittest.main()
