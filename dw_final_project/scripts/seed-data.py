"""Seed script to populate the warehouse with sample data for development."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from datetime import date, datetime, timedelta, UTC
from database.connection import init_cassandra
from database.init_schema import create_tables
from repositories.asset_repository import AssetRepository
from repositories.data_source_repository import DataSourceRepository
from repositories.time_series_repository import TimeSeriesRepository
from models.asset_model import AssetModel
from models.data_source_model import DataSourceModel
from models.time_series_model import TimeSeriesRecord
import random


def seed():
    init_cassandra()
    create_tables()

    asset_repo = AssetRepository()
    ds_repo = DataSourceRepository()
    ts_repo = TimeSeriesRepository()

    # Create data source
    ds_repo.save(DataSourceModel(
        id="YFINANCE",
        system_date=datetime.now(UTC),
        name="Yahoo Finance",
        description="Market data via yfinance (no API key required)",
        attributes={"Open", "Close", "High", "Low", "Volume"},
    ))

    # Create sample assets
    assets = [
        ("YFINANCE/AAPL", "AAPL", "Apple Inc stock data"),
        ("YFINANCE/GOOGL", "GOOGL", "Alphabet Inc stock data"),
        ("YFINANCE/MSFT", "MSFT", "Microsoft Corp stock data"),
        ("YFINANCE/BTC-USD", "BTC-USD", "Bitcoin/USD pair"),
    ]

    for asset_id, name, desc in assets:
        asset_repo.save(AssetModel(
            id=asset_id,
            system_date=datetime.now(UTC),
            name=name,
            description=desc,
            attributes={"type": "crypto" if "BTC" in asset_id else "stock"},
        ))

    # Generate time series data
    base_date = date(2024, 1, 1)
    for asset_id, name, _ in assets:
        records = []
        price = random.uniform(100, 50000)
        for i in range(200):
            bdate = base_date + timedelta(days=i)
            change = random.gauss(0, price * 0.02)
            open_p = price
            close_p = price + change
            high_p = max(open_p, close_p) + abs(random.gauss(0, price * 0.005))
            low_p = min(open_p, close_p) - abs(random.gauss(0, price * 0.005))
            volume = random.randint(1000000, 50000000)
            price = close_p

            records.append(TimeSeriesRecord(
                asset_id=asset_id,
                data_source_id="YFINANCE",
                business_date_year=bdate.year,
                business_date=bdate,
                system_date=datetime.now(UTC),
                values_double={
                    "Open": round(open_p, 2),
                    "Close": round(close_p, 2),
                    "High": round(high_p, 2),
                    "Low": round(low_p, 2),
                },
                values_int={"Volume": volume},
            ))

        ts_repo.save_batch(records[:50])
        ts_repo.save_batch(records[50:100])
        ts_repo.save_batch(records[100:150])
        ts_repo.save_batch(records[150:])

    print(f"Seeded {len(assets)} assets with 200 days of data each.")


if __name__ == "__main__":
    seed()
