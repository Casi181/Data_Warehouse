"""Yahoo Finance data provider using the yfinance library.

No API key required. Fetches OHLCV historical data for any ticker symbol
supported by Yahoo Finance (NASDAQ, NYSE, crypto, etc.).
"""

import asyncio
import logging
from datetime import datetime

import yfinance as yf

from etl.extractor import RawPage

logger = logging.getLogger(__name__)

# Standard columns returned by this provider
YFINANCE_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]


class YFinanceClient:
    """Fetches historical daily OHLCV data via yfinance.

    Since yfinance is synchronous, calls are run in a thread executor
    to avoid blocking the async event loop.
    """

    async def fetch_dataset(
        self,
        dataset_code: str,
        cursor: str | None = None,
        period: str = "1y",
    ) -> RawPage:
        """Fetch historical data for a ticker symbol.

        Args:
            dataset_code: Ticker symbol (e.g. "AAPL", "MSFT", "BTC-USD").
            cursor: Unused -- yfinance returns all data in one call.
            period: How much history to fetch. Valid values:
                    "1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max".
                    Defaults to "1y".

        Returns:
            RawPage with OHLCV records, one per trading day.
        """
        ticker = dataset_code.strip().upper()

        # Run the synchronous yfinance call off the event loop
        df = await asyncio.to_thread(self._download, ticker, period)

        if df is None or df.empty:
            logger.warning("No data returned for ticker %s (period=%s)", ticker, period)
            return RawPage(
                records=[],
                columns=YFINANCE_COLUMNS,
                next_cursor=None,
                record_count=0,
            )

        records: list[dict] = []
        for idx, row in df.iterrows():
            try:
                # idx is a pandas Timestamp
                dt_str = idx.strftime("%Y-%m-%d")
                records.append({
                    "Date": dt_str,
                    "Open": float(row["Open"]),
                    "High": float(row["High"]),
                    "Low": float(row["Low"]),
                    "Close": float(row["Close"]),
                    "Volume": int(row["Volume"]),
                })
            except (KeyError, ValueError, TypeError) as exc:
                logger.debug("Skipping row for %s: %s", ticker, exc)
                continue

        logger.info(
            "Fetched %d records for %s (period=%s)", len(records), ticker, period
        )

        return RawPage(
            records=records,
            columns=YFINANCE_COLUMNS,
            next_cursor=None,  # yfinance has no pagination
            record_count=len(records),
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _download(ticker: str, period: str):
        """Synchronous yfinance download (runs in a thread)."""
        try:
            tk = yf.Ticker(ticker)
            df = tk.history(period=period, interval="1d", auto_adjust=True)
            return df
        except Exception as exc:
            logger.error("yfinance download failed for %s: %s", ticker, exc)
            return None
