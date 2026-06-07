from repositories.asset_repository import AssetRepository
from repositories.data_source_repository import DataSourceRepository
from repositories.time_series_repository import TimeSeriesRepository
from models.asset_model import AssetModel
from models.data_source_model import DataSourceModel
from models.time_series_model import TimeSeriesRecord
from datetime import datetime, UTC

# Rich metadata for known tickers per the project spec:
# class (stock/crypto/commodity/etf/index), name, region, exchange
_METADATA: dict[str, dict[str, str]] = {
    "AAPL": {"class": "stock", "name": "Apple Inc.", "region": "US", "exchange": "NASDAQ"},
    "MSFT": {"class": "stock", "name": "Microsoft Corp.", "region": "US", "exchange": "NASDAQ"},
    "GOOGL": {"class": "stock", "name": "Alphabet Inc.", "region": "US", "exchange": "NASDAQ"},
    "AMZN": {"class": "stock", "name": "Amazon.com Inc.", "region": "US", "exchange": "NASDAQ"},
    "NVDA": {"class": "stock", "name": "NVIDIA Corp.", "region": "US", "exchange": "NASDAQ"},
    "META": {"class": "stock", "name": "Meta Platforms Inc.", "region": "US", "exchange": "NASDAQ"},
    "TSLA": {"class": "stock", "name": "Tesla Inc.", "region": "US", "exchange": "NASDAQ"},
    "BRK-B": {"class": "stock", "name": "Berkshire Hathaway B", "region": "US", "exchange": "NYSE"},
    "JPM": {"class": "stock", "name": "JPMorgan Chase & Co.", "region": "US", "exchange": "NYSE"},
    "V": {"class": "stock", "name": "Visa Inc.", "region": "US", "exchange": "NYSE"},
    "JNJ": {"class": "stock", "name": "Johnson & Johnson", "region": "US", "exchange": "NYSE"},
    "WMT": {"class": "stock", "name": "Walmart Inc.", "region": "US", "exchange": "NYSE"},
    "PG": {"class": "stock", "name": "Procter & Gamble Co.", "region": "US", "exchange": "NYSE"},
    "MA": {"class": "stock", "name": "Mastercard Inc.", "region": "US", "exchange": "NYSE"},
    "HD": {"class": "stock", "name": "The Home Depot Inc.", "region": "US", "exchange": "NYSE"},
    "DIS": {"class": "stock", "name": "The Walt Disney Co.", "region": "US", "exchange": "NYSE"},
    "NFLX": {"class": "stock", "name": "Netflix Inc.", "region": "US", "exchange": "NASDAQ"},
    "ADBE": {"class": "stock", "name": "Adobe Inc.", "region": "US", "exchange": "NASDAQ"},
    "CRM": {"class": "stock", "name": "Salesforce Inc.", "region": "US", "exchange": "NYSE"},
    "INTC": {"class": "stock", "name": "Intel Corp.", "region": "US", "exchange": "NASDAQ"},
    "AMD": {"class": "stock", "name": "Advanced Micro Devices", "region": "US", "exchange": "NASDAQ"},
    "PYPL": {"class": "stock", "name": "PayPal Holdings Inc.", "region": "US", "exchange": "NASDAQ"},
    "BA": {"class": "stock", "name": "The Boeing Company", "region": "US", "exchange": "NYSE"},
    "GS": {"class": "stock", "name": "Goldman Sachs Group", "region": "US", "exchange": "NYSE"},
    "IBM": {"class": "stock", "name": "IBM Corp.", "region": "US", "exchange": "NYSE"},
    "BTC-USD": {"class": "cryptocurrency", "name": "Bitcoin", "region": "Global", "exchange": "Crypto"},
    "ETH-USD": {"class": "cryptocurrency", "name": "Ethereum", "region": "Global", "exchange": "Crypto"},
    "SOL-USD": {"class": "cryptocurrency", "name": "Solana", "region": "Global", "exchange": "Crypto"},
    "XRP-USD": {"class": "cryptocurrency", "name": "XRP", "region": "Global", "exchange": "Crypto"},
    "ADA-USD": {"class": "cryptocurrency", "name": "Cardano", "region": "Global", "exchange": "Crypto"},
    "GC=F": {"class": "commodity", "name": "Gold Futures", "region": "Global", "exchange": "COMEX"},
    "SI=F": {"class": "commodity", "name": "Silver Futures", "region": "Global", "exchange": "COMEX"},
    "CL=F": {"class": "commodity", "name": "Crude Oil Futures", "region": "Global", "exchange": "NYMEX"},
    "GLD": {"class": "etf", "name": "SPDR Gold Shares", "region": "US", "exchange": "NYSE Arca"},
    "SPY": {"class": "index", "name": "S&P 500 ETF Trust", "region": "US", "exchange": "NYSE Arca"},
    "QQQ": {"class": "index", "name": "Invesco QQQ Trust", "region": "US", "exchange": "NASDAQ"},
    "TSM": {"class": "stock", "name": "Taiwan Semiconductor", "region": "Asia", "exchange": "NYSE"},
    "BABA": {"class": "stock", "name": "Alibaba Group", "region": "Asia", "exchange": "NYSE"},
    "NVO": {"class": "stock", "name": "Novo Nordisk A/S", "region": "Europe", "exchange": "NYSE"},
    "SAP": {"class": "stock", "name": "SAP SE", "region": "Europe", "exchange": "NYSE"},
    "TM": {"class": "stock", "name": "Toyota Motor Corp.", "region": "Asia", "exchange": "NYSE"},
    # Bitfinex tickers
    "BTC/USD": {"class": "cryptocurrency", "name": "Bitcoin", "region": "Global", "exchange": "Bitfinex"},
    "ETH/USD": {"class": "cryptocurrency", "name": "Ethereum", "region": "Global", "exchange": "Bitfinex"},
}


def _get_asset_attrs(dataset_code: str, provider: str) -> dict[str, str]:
    """Build attributes dict for an asset from metadata or defaults."""
    meta = _METADATA.get(dataset_code, {})
    return {
        "symbol": dataset_code,
        "class": meta.get("class", "unknown"),
        "region": meta.get("region", "Unknown"),
        "exchange": meta.get("exchange", "Unknown"),
        "provider": provider,
    }


class Loader:
    def __init__(
        self,
        asset_repo: AssetRepository,
        ds_repo: DataSourceRepository,
        ts_repo: TimeSeriesRepository,
    ):
        self._asset_repo = asset_repo
        self._ds_repo = ds_repo
        self._ts_repo = ts_repo

    def load(
        self,
        records: list[TimeSeriesRecord],
        dataset_code: str,
        provider: str,
        columns: list[str],
    ) -> int:
        if not records:
            return 0

        asset_id = dataset_code
        if self._asset_repo.find_latest(asset_id) is None:
            meta = _METADATA.get(dataset_code, {})
            self._asset_repo.save(
                AssetModel(
                    id=asset_id,
                    system_date=datetime.now(UTC),
                    name=meta.get("name", dataset_code),
                    description=f"{meta.get('class', 'asset').title()} — {meta.get('exchange', provider)}",
                    attributes=_get_asset_attrs(dataset_code, provider),
                )
            )

        if self._ds_repo.find_latest(provider) is None:
            self._ds_repo.save(
                DataSourceModel(
                    id=provider,
                    system_date=datetime.now(UTC),
                    name=provider,
                    description=f"Data provider {provider}",
                    attributes=set(
                        c for c in columns if c.lower() != "date"
                    ),
                )
            )

        return self._ts_repo.save_batch(records)
