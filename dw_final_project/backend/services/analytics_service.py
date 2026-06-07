from config.settings import get_settings
from schemas.analytics_schemas import SparkJobResult
import logging
import traceback

logger = logging.getLogger(__name__)


class AnalyticsService:
    def run_aggregation(self, data_source_id: str) -> SparkJobResult:
        try:
            from spark.aggregation import run_aggregation

            settings = get_settings()
            hosts = settings.cassandra_hosts.split(",")[0].strip()
            count = run_aggregation(hosts, settings.cassandra_keyspace, data_source_id)
            return SparkJobResult(
                status="completed",
                rows_processed=count,
                message=f"Aggregation complete: {count} rows",
            )
        except Exception as e:
            logger.error("Aggregation failed: %s\n%s", e, traceback.format_exc())
            return SparkJobResult(
                status="failed", rows_processed=0, message=str(e)
            )

    def run_prediction(
        self, asset_id: str, data_source_id: str
    ) -> SparkJobResult:
        try:
            from spark.prediction import run_prediction

            settings = get_settings()
            hosts = settings.cassandra_hosts.split(",")[0].strip()
            result = run_prediction(
                hosts, settings.cassandra_keyspace, asset_id, data_source_id
            )

            count = result["count"]
            metrics = result.get("metrics")

            # Build a descriptive message including key metrics
            msg_parts = [f"Prediction complete: {count} rows"]
            if metrics:
                msg_parts.append(
                    f"Model: {metrics.get('model_type', 'N/A')}, "
                    f"RMSE: {metrics.get('rmse', 'N/A')}, "
                    f"R2: {metrics.get('r2', 'N/A')}, "
                    f"MAE: {metrics.get('mae', 'N/A')}"
                )

            return SparkJobResult(
                status="completed",
                rows_processed=count,
                message=" | ".join(msg_parts),
                metrics=metrics,
            )
        except Exception as e:
            logger.error("Prediction failed: %s\n%s", e, traceback.format_exc())
            return SparkJobResult(
                status="failed", rows_processed=0, message=str(e)
            )
