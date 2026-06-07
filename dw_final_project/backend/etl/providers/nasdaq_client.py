import httpx
from config.settings import get_settings
from etl.extractor import RawPage


class NasdaqClient:
    BASE_URL = "https://data.nasdaq.com/api/v3/datatables"

    async def fetch_dataset(
        self, dataset_code: str, cursor: str | None = None
    ) -> RawPage:
        settings = get_settings()
        params: dict = {
            "api_key": settings.nasdaq_api_key,
            "qopts.per_page": 100,
        }
        if cursor:
            params["qopts.cursor_id"] = cursor

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.BASE_URL}/{dataset_code}.json", params=params
            )
            resp.raise_for_status()
            body = resp.json()

        table = body.get("datatable", {})
        columns = [c["name"] for c in table.get("columns", [])]
        raw_rows = table.get("data", [])
        records = [dict(zip(columns, row)) for row in raw_rows]
        next_cursor = body.get("meta", {}).get("next_cursor_id")

        return RawPage(
            records=records,
            columns=columns,
            next_cursor=next_cursor,
            record_count=len(records),
        )
