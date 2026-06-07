"""Unit tests for schemas and DTOs."""
import unittest


class TestSchemas(unittest.TestCase):
    def test_paginated_response(self):
        from schemas.common_schemas import PaginatedResponse

        resp = PaginatedResponse(
            items=["a", "b"], offset=0, limit=20, total=2, has_next=False
        )
        self.assertEqual(len(resp.items), 2)
        self.assertFalse(resp.has_next)

    def test_ingestion_request(self):
        from schemas.ingestion_schemas import IngestionRequest

        req = IngestionRequest(
            provider="YFINANCE",
            dataset_codes=["AAPL"],
        )
        self.assertEqual(req.provider, "YFINANCE")
        self.assertEqual(len(req.dataset_codes), 1)

    def test_analytics_schemas(self):
        from schemas.analytics_schemas import (
            AggregateRequest, PredictRequest, SparkJobResult
        )

        agg = AggregateRequest(data_source_id="YFINANCE")
        pred = PredictRequest(asset_id="test", data_source_id="YFINANCE")
        result = SparkJobResult(status="completed", rows_processed=10, message="ok")
        self.assertEqual(agg.data_source_id, "YFINANCE")
        self.assertEqual(pred.asset_id, "test")
        self.assertEqual(result.rows_processed, 10)
        self.assertIsNone(result.metrics)

    def test_spark_job_result_with_metrics(self):
        from schemas.analytics_schemas import SparkJobResult

        metrics = {
            "rmse": 2.345,
            "mae": 1.567,
            "r2": 0.923,
            "model_type": "GBTRegressor",
            "train_count": 140,
            "test_count": 60,
            "best_max_depth": 5,
            "best_max_iter": 50,
            "best_step_size": 0.1,
            "features": [
                "seconds", "close", "low", "high",
                "daily_return", "price_range", "range_pct",
                "hl_ratio", "close_lag_1", "return_lag_1",
            ],
            "cv_folds": 3,
        }
        result = SparkJobResult(
            status="completed",
            rows_processed=60,
            message="Prediction complete: 60 rows | Model: GBTRegressor, RMSE: 2.345",
            metrics=metrics,
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.metrics["rmse"], 2.345)
        self.assertEqual(result.metrics["model_type"], "GBTRegressor")
        self.assertEqual(result.metrics["r2"], 0.923)
        self.assertEqual(len(result.metrics["features"]), 10)
        self.assertEqual(result.metrics["cv_folds"], 3)

    def test_asset_detail_from_model(self):
        from schemas.asset_schemas import AssetDetail
        from models.asset_model import AssetModel
        from datetime import datetime

        model = AssetModel(
            id="test", system_date=datetime(2024, 1, 1),
            name="Test", description="A test",
            attributes={"type": "stock"},
        )
        detail = AssetDetail.from_model(model)
        self.assertEqual(detail.id, "test")
        self.assertEqual(detail.name, "Test")
        self.assertIn("type", detail.attributes)


if __name__ == "__main__":
    unittest.main()
