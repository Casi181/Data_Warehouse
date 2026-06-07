from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def run_aggregation(
    cassandra_host: str, keyspace: str, data_source_filter: str
) -> int:
    spark = (
        SparkSession.builder.appName("Casi DW - Aggregation")
        .config("spark.cassandra.connection.host", cassandra_host)
        .config(
            "spark.jars.packages",
            "com.datastax.spark:spark-cassandra-connector_2.13:3.5.1",
        )
        .getOrCreate()
    )

    df = (
        spark.read.format("org.apache.spark.sql.cassandra")
        .options(table="data", keyspace=keyspace)
        .load()
    )

    # Use DataFrame API instead of SQL string interpolation to prevent injection
    totals_df = (
        df.filter(F.col("data_source_id") == data_source_filter)
        .groupBy("asset_id", "business_date_year")
        .agg(F.count("*").alias("cnt"))
    )

    # Cache to avoid recomputing the DAG for both write and count
    totals_df = totals_df.cache()
    row_count = totals_df.count()

    (
        totals_df.write.format("org.apache.spark.sql.cassandra")
        .options(table="totals", keyspace=keyspace)
        .mode("append")
        .save()
    )

    totals_df.unpersist()
    spark.stop()
    return row_count
