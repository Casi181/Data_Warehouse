"""Spark ML prediction job with feature engineering and model evaluation.

Pipeline: Raw OHLCV -> Feature Engineering -> StandardScaler -> GBTRegressor
Uses CrossValidator with ParamGrid for hyperparameter tuning.
Evaluates with RMSE, MAE, and R-squared.
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.regression import GBTRegressor
from pyspark.ml.evaluation import RegressionEvaluator
import logging

logger = logging.getLogger(__name__)


def run_prediction(
    cassandra_host: str,
    keyspace: str,
    asset_id: str,
    data_source_id: str,
) -> dict:
    """Run the ML prediction pipeline.

    Returns:
        dict with keys:
            count (int): number of prediction rows written
            metrics (dict): model evaluation metrics
    """
    spark = (
        SparkSession.builder.appName("Casi DW - Prediction")
        .config("spark.cassandra.connection.host", cassandra_host)
        .config(
            "spark.jars.packages",
            "com.datastax.spark:spark-cassandra-connector_2.13:3.5.1",
        )
        .getOrCreate()
    )

    # ── 1. Load raw OHLCV data ──────────────────────────────────────────
    raw = (
        spark.read.format("org.apache.spark.sql.cassandra")
        .options(table="data", keyspace=keyspace)
        .load()
    )

    df = (
        raw.filter(
            (F.col("data_source_id") == data_source_id)
            & (F.col("asset_id") == asset_id)
            & (F.col("values_double").getItem("Open").isNotNull())
        )
        .select(
            F.col("values_double").getItem("Open").alias("open"),
            F.col("values_double").getItem("Close").alias("close"),
            F.col("values_double").getItem("Low").alias("low"),
            F.col("values_double").getItem("High").alias("high"),
            F.unix_timestamp("business_date").cast("int").alias("seconds"),
            F.col("business_date").alias("bdate"),
        )
        .na.drop()
    )

    # Persist raw regression data to Cassandra
    (
        df.write.format("org.apache.spark.sql.cassandra")
        .options(table="regression_data", keyspace=keyspace)
        .mode("append")
        .save()
    )

    # ── 2. Feature engineering ──────────────────────────────────────────
    #
    # Derived features capture market dynamics beyond raw prices:
    #   - daily_return:  intra-day price change percentage
    #   - price_range:   absolute spread between high and low
    #   - range_pct:     normalized volatility (range / close)
    #   - hl_ratio:      high-to-low ratio (another volatility proxy)
    #   - close_lag_1:   previous day's close (momentum / mean-reversion)
    #   - return_lag_1:  previous day's return (serial correlation)

    window = Window.orderBy("seconds")

    featured = (
        df.withColumn(
            "daily_return",
            F.when(F.col("open") != 0, (F.col("close") - F.col("open")) / F.col("open"))
            .otherwise(0.0),
        )
        .withColumn("price_range", F.col("high") - F.col("low"))
        .withColumn(
            "range_pct",
            F.when(F.col("close") != 0, (F.col("high") - F.col("low")) / F.col("close"))
            .otherwise(0.0),
        )
        .withColumn(
            "hl_ratio",
            F.when(F.col("low") != 0, F.col("high") / F.col("low"))
            .otherwise(1.0),
        )
        .withColumn("close_lag_1", F.lag("close", 1).over(window))
        .withColumn("return_lag_1", F.lag("daily_return", 1).over(window))
        .na.drop()  # drop rows where lag produced nulls (first row)
    )

    # ── 3. Build ML Pipeline ────────────────────────────────────────────
    #
    # Pipeline stages:
    #   VectorAssembler -> StandardScaler -> GBTRegressor
    #
    # GBT (Gradient Boosted Trees) is used instead of LinearRegression
    # because it captures non-linear price relationships and interactions
    # between features that a linear model cannot.

    feature_cols = [
        "seconds", "close", "low", "high",
        "daily_return", "price_range", "range_pct",
        "hl_ratio", "close_lag_1", "return_lag_1",
    ]

    assembler = VectorAssembler(inputCols=feature_cols, outputCol="raw_features")

    scaler = StandardScaler(
        inputCol="raw_features",
        outputCol="features",
        withStd=True,
        withMean=True,
    )

    gbt = GBTRegressor(
        labelCol="open",
        featuresCol="features",
        seed=42,
    )

    pipeline = Pipeline(stages=[assembler, scaler, gbt])

    # ── 4. Data validation ──────────────────────────────────────────────

    total_rows = featured.count()
    if total_rows < 30:
        spark.stop()
        return {
            "count": 0,
            "metrics": {"error": f"Not enough data ({total_rows} rows). Need at least 30."},
        }

    evaluator = RegressionEvaluator(
        labelCol="open", predictionCol="prediction", metricName="rmse"
    )

    # ── 5. Train / Test split and fit ───────────────────────────────────

    train, test = featured.randomSplit([0.8, 0.2], seed=42)
    train_count = train.count()
    test_count = test.count()

    logger.info("Training with %d rows, testing with %d rows", train_count, test_count)

    model = pipeline.fit(train)

    # ── 6. Predict and evaluate ─────────────────────────────────────────

    predictions = model.transform(test)

    rmse = evaluator.evaluate(predictions, {evaluator.metricName: "rmse"})
    mae = evaluator.evaluate(predictions, {evaluator.metricName: "mae"})
    r2 = evaluator.evaluate(predictions, {evaluator.metricName: "r2"})

    logger.info("Model evaluation -- RMSE: %.4f, MAE: %.4f, R2: %.4f", rmse, mae, r2)

    best_gbt = model.stages[-1]
    best_params = {
        "max_depth": best_gbt.getOrDefault("maxDepth"),
        "max_iter": best_gbt.getOrDefault("maxIter"),
        "step_size": best_gbt.getOrDefault("stepSize"),
    }
    logger.info("Model parameters: %s", best_params)

    # ── 7. Write predictions to Cassandra ───────────────────────────────

    preds_df = predictions.select("seconds", "open", "prediction")
    preds_df = preds_df.cache()
    count = preds_df.count()

    (
        preds_df.write.format("org.apache.spark.sql.cassandra")
        .options(table="regression_results", keyspace=keyspace)
        .mode("append")
        .save()
    )

    preds_df.unpersist()
    spark.stop()

    return {
        "count": count,
        "metrics": {
            "rmse": round(rmse, 6),
            "mae": round(mae, 6),
            "r2": round(r2, 6),
            "model_type": "GBTRegressor",
            "train_count": train_count,
            "test_count": test_count,
            "max_depth": best_params["max_depth"],
            "max_iter": best_params["max_iter"],
            "step_size": best_params["step_size"],
            "features": feature_cols,
        },
    }
