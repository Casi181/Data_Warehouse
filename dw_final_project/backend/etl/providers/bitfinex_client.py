import httpx
from etl.extractor import RawPage


class BitfinexClient:
    BASE_URL = "https://api-pub.bitfinex.com/v2"

    async def fetch_dataset(
        self, dataset_code: str, cursor: str | None = None
    ) -> RawPage:
        symbol = dataset_code.replace("/", "")
        params: dict = {"limit": 100, "sort": -1}

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.BASE_URL}/candles/trade:1D:t{symbol}/hist",
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

        columns = ["date", "Open", "Close", "High", "Low", "Volume"]
        records = []
        for row in data:
            if len(row) >= 6:
                from datetime import datetime, timezone

                ts = row[0] / 1000
                dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
                records.append({
                    "date": dt,
                    "Open": row[1],
                    "Close": row[2],
                    "High": row[3],
                    "Low": row[4],
                    "Volume": row[5],
                })

        return RawPage(
            records=records,
            columns=columns,
            next_cursor=None,
            record_count=len(records),
        )
