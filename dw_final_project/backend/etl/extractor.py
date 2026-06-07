from dataclasses import dataclass


@dataclass
class RawPage:
    records: list[dict]
    columns: list[str]
    next_cursor: str | None
    record_count: int


class Extractor:
    def __init__(self):
        from etl.providers.yfinance_client import YFinanceClient
        from etl.providers.nasdaq_client import NasdaqClient
        from etl.providers.bitfinex_client import BitfinexClient

        self._clients = {
            "YFINANCE": YFinanceClient(),
            "NASDAQ-DATA-LINK": NasdaqClient(),
            "BITFINEX": BitfinexClient(),
        }

    async def fetch(
        self,
        provider: str,
        dataset_code: str,
        cursor: str | None = None,
        period: str = "1y",
    ) -> RawPage:
        client = self._clients.get(provider)
        if not client:
            raise ValueError(f"Unknown provider: {provider}")
        # YFinanceClient accepts an extra 'period' kwarg
        if provider == "YFINANCE":
            return await client.fetch_dataset(dataset_code, cursor, period=period)
        return await client.fetch_dataset(dataset_code, cursor)
