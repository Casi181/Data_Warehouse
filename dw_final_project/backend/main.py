from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.connection import init_cassandra, shutdown_cassandra
from database.init_schema import create_tables
from routers import assets, data_sources, data, ingestion, analytics
from middleware.error_handler import global_exception_handler
from middleware.request_logging import RequestLoggingMiddleware
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tickers to auto-ingest on startup for a stock-exchange look
AUTO_INGEST_TICKERS = [
    # US Large-Cap Stocks
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "JPM", "V", "JNJ", "WMT", "PG", "MA", "HD", "DIS", "NFLX", "ADBE",
    "CRM", "INTC", "AMD", "PYPL", "BA", "GS", "IBM",
    # Crypto
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD",
    # Commodities / ETFs
    "GC=F", "SI=F", "CL=F", "GLD", "SPY", "QQQ",
    # International
    "TSM", "BABA", "NVO", "SAP", "TM",
]


async def _auto_ingest():
    """Background task to seed the database with financial data on first start."""
    from etl.extractor import Extractor
    from etl.transformer import Transformer
    from etl.loader import Loader
    from repositories.asset_repository import AssetRepository
    from repositories.data_source_repository import DataSourceRepository
    from repositories.time_series_repository import TimeSeriesRepository
    from schemas.ingestion_schemas import IngestionRequest

    # Check which tickers still need ingestion
    asset_repo = AssetRepository()
    existing_ids, _ = asset_repo.find_all_ids_paginated(limit=1000)
    missing = [t for t in AUTO_INGEST_TICKERS if t not in existing_ids]
    if not missing:
        logger.info("All %d tickers already ingested, skipping.", len(AUTO_INGEST_TICKERS))
        return

    logger.info("Ingesting %d missing tickers...", len(missing))

    extractor = Extractor()
    transformer = Transformer()
    loader = Loader(
        asset_repo=asset_repo,
        ds_repo=DataSourceRepository(),
        ts_repo=TimeSeriesRepository(),
    )
    from services.ingestion_service import IngestionService
    service = IngestionService(extractor, transformer, loader)

    # Ingest from YFINANCE (primary provider)
    request = IngestionRequest(
        provider="YFINANCE",
        dataset_codes=missing,
        period="2y",
    )
    result = await service.run_ingestion(request)
    logger.info(
        "YFINANCE ingestion done: fetched=%d, stored=%d, errors=%d",
        result.fetched, result.stored, result.errors,
    )

    # Ingest from BITFINEX (second provider) to demonstrate heterogeneous multi-provider data
    bitfinex_tickers = ["BTC/USD", "ETH/USD"]
    bitfinex_missing = [t for t in bitfinex_tickers if t not in existing_ids]
    if bitfinex_missing:
        logger.info("Ingesting %d tickers from BITFINEX...", len(bitfinex_missing))
        bitfinex_req = IngestionRequest(
            provider="BITFINEX",
            dataset_codes=bitfinex_missing,
            period="1y",
        )
        bf_result = await service.run_ingestion(bitfinex_req)
        logger.info(
            "BITFINEX ingestion done: fetched=%d, stored=%d, errors=%d",
            bf_result.fetched, bf_result.stored, bf_result.errors,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_cassandra()
    create_tables()
    asyncio.create_task(_auto_ingest())
    yield
    shutdown_cassandra()


app = FastAPI(
    title="Casi Financial Data Warehouse",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(assets.router)
app.include_router(data_sources.router)
app.include_router(data.router)
app.include_router(ingestion.router)
app.include_router(analytics.router)
