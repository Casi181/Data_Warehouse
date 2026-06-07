"""Unit tests for model data classes."""
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, date, UTC
from models.asset_model import AssetModel
from models.data_source_model import DataSourceModel
from models.time_series_model import TimeSeriesRecord


class TestAssetModel(unittest.TestCase):
    def test_is_deleted_true(self):
        model = AssetModel(
            id="test", system_date=datetime.now(UTC),
            attributes={"deleted": "true"}
        )
        self.assertTrue(model.is_deleted)

    def test_is_deleted_false(self):
        model = AssetModel(
            id="test", system_date=datetime.now(UTC),
            attributes={"type": "stock"}
        )
        self.assertFalse(model.is_deleted)

    def test_is_deleted_empty(self):
        model = AssetModel(id="test", system_date=datetime.now(UTC))
        self.assertFalse(model.is_deleted)


class TestDataSourceModel(unittest.TestCase):
    def test_creation(self):
        model = DataSourceModel(
            id="YFINANCE", system_date=datetime.now(UTC),
            name="Yahoo Finance", description="Provider",
            attributes={"Open", "Close"}
        )
        self.assertEqual(model.id, "YFINANCE")
        self.assertEqual(len(model.attributes), 2)


class TestTimeSeriesRecord(unittest.TestCase):
    def test_creation(self):
        rec = TimeSeriesRecord(
            asset_id="YFINANCE/AAPL",
            data_source_id="YFINANCE",
            business_date_year=2024,
            business_date=date(2024, 6, 1),
            system_date=datetime.now(UTC),
            values_double={"Open": 150.0, "Close": 151.0},
        )
        self.assertEqual(rec.asset_id, "YFINANCE/AAPL")
        self.assertFalse(rec.deleted)
        self.assertEqual(rec.values_double["Open"], 150.0)

    def test_default_empty_collections(self):
        rec = TimeSeriesRecord(
            asset_id="test",
            data_source_id="src",
            business_date_year=2024,
            business_date=date(2024, 1, 1),
            system_date=datetime.now(UTC),
        )
        self.assertEqual(rec.values_double, {})
        self.assertEqual(rec.values_int, {})
        self.assertEqual(rec.values_text, {})


if __name__ == "__main__":
    unittest.main()
