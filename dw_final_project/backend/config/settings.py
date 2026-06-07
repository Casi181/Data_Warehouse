from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    cassandra_hosts: str = "localhost"
    cassandra_port: int = 9042
    cassandra_keyspace: str = "acme_dw"
    nasdaq_api_key: str = ""  # kept for backward compat; not required by yfinance
    spark_master: str = "spark://localhost:7077"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
