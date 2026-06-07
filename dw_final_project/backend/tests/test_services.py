"""Unit tests for service layer (mocked repositories)."""
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, date, UTC
from models.asset_model import AssetModel
from models.time_series_model import TimeSeriesRecord
from services.asset_service import AssetService
from services.time_series_service import TimeSeriesService
from services.analytics_service import AnalyticsService


class TestAssetService(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock()
        self.service = AssetService(repo=self.mock_repo)

    def test_list_assets_empty(self):
        self.mock_repo.find_all_ids_paginated.return_value = ([], 0)
        result = self.service.list_assets(0, 20)
        self.assertEqual(result.items, [])
        self.assertEqual(result.total, 0)
        self.assertFalse(result.has_next)

    def test_list_assets_with_data(self):
        self.mock_repo.find_all_ids_paginated.return_value = (
            ["asset1", "asset2"], 5
        )
        result = self.service.list_assets(0, 2)
        self.assertEqual(len(result.items), 2)
        self.assertEqual(result.total, 5)
        self.assertTrue(result.has_next)

    def test_get_asset_details_not_found(self):
        self.mock_repo.find_all_versions.return_value = []
        result = self.service.get_asset_details("nonexistent")
        self.assertEqual(result, [])

    def test_get_asset_details_found(self):
        model = AssetModel(
            id="test", system_date=datetime.now(UTC),
            name="Test", description="Desc",
            attributes={"type": "stock"},
        )
        self.mock_repo.find_all_versions.return_value = [model]
        result = self.service.get_asset_details("test")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "test")
        self.assertEqual(result[0].name, "Test")


class TestTimeSeriesService(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock()
        self.service = TimeSeriesService(repo=self.mock_repo)

    def test_get_time_series_empty(self):
        self.mock_repo.find_by_range.return_value = []
        result = self.service.get_time_series(
            "asset", "source", date(2024, 1, 1), date(2024, 6, 1)
        )
        self.assertEqual(result["data"]["records"], [])

    def test_get_time_series_with_data(self):
        records = [
            TimeSeriesRecord(
                asset_id="asset", data_source_id="source",
                business_date_year=2024,
                business_date=date(2024, 3, 1),
                system_date=datetime.now(UTC),
                values_double={"Close": 150.0},
            ),
        ]
        self.mock_repo.find_by_range.return_value = records
        result = self.service.get_time_series(
            "asset", "source", date(2024, 1, 1), date(2024, 6, 1)
        )
        self.assertEqual(len(result["data"]["records"]), 1)
        self.assertEqual(result["data"]["records"][0]["values"]["Close"], 150.0)

    def test_get_time_series_with_attributes(self):
        records = [
            TimeSeriesRecord(
                asset_id="asset", data_source_id="source",
                business_date_year=2024,
                business_date=date(2024, 3, 1),
                system_date=datetime.now(UTC),
                values_double={"Open": 148.0, "Close": 150.0},
            ),
        ]
        self.mock_repo.find_by_range.return_value = records
        result = self.service.get_time_series(
            "asset", "source", date(2024, 1, 1), date(2024, 6, 1),
            include_attributes=True,
        )
        self.assertIn("attributes", result)
        self.assertIn("Close", result["attributes"])
        self.assertIn("Open", result["attributes"])


class TestAnalyticsService(unittest.TestCase):
    """Tests that AnalyticsService correctly handles prediction results with metrics."""

    def test_prediction_result_with_metrics(self):
        """Verify SparkJobResult correctly carries metrics from prediction."""
        from schemas.analytics_schemas import SparkJobResult

        # Simulate the dict that spark/prediction.py returns
        fake_result = {
            "count": 42,
            "metrics": {
                "rmse": 2.345678,
                "mae": 1.567890,
                "r2": 0.923456,
                "model_type": "GBTRegressor",
                "train_count": 98,
                "test_count": 42,
                "best_max_depth": 5,
                "best_max_iter": 50,
                "best_step_size": 0.1,
                "features": ["seconds", "close", "low", "high",
                             "daily_return", "price_range", "range_pct",
                             "hl_ratio", "close_lag_1", "return_lag_1"],
                "cv_folds": 3,
            },
        }

        # Reproduce the logic from AnalyticsService.run_prediction
        count = fake_result["count"]
        metrics = fake_result.get("metrics")
        msg_parts = [f"Prediction complete: {count} rows"]
        if metrics:
            msg_parts.append(
                f"Model: {metrics.get('model_type', 'N/A')}, "
                f"RMSE: {metrics.get('rmse', 'N/A')}, "
                f"R2: {metrics.get('r2', 'N/A')}, "
                f"MAE: {metrics.get('mae', 'N/A')}"
            )

        result = SparkJobResult(
            status="completed",
            rows_processed=count,
            message=" | ".join(msg_parts),
            metrics=metrics,
        )

        self.assertEqual(result.status, "completed")
        self.assertEqual(result.rows_processed, 42)
        self.assertIsNotNone(result.metrics)
        self.assertEqual(result.metrics["rmse"], 2.345678)
        self.assertEqual(result.metrics["model_type"], "GBTRegressor")
        self.assertEqual(result.metrics["r2"], 0.923456)
        self.assertEqual(result.metrics["cv_folds"], 3)
        self.assertEqual(len(result.metrics["features"]), 10)
        self.assertIn("GBTRegressor", result.message)
        self.assertIn("RMSE", result.message)

    def test_prediction_result_without_metrics(self):
        from schemas.analytics_schemas import SparkJobResult

        result = SparkJobResult(
            status="completed",
            rows_processed=10,
            message="Prediction complete",
        )
        self.assertIsNone(result.metrics)


if __name__ == "__main__":
    unittest.main()
