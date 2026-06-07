from etl.extractor import Extractor
from etl.transformer import Transformer
from etl.loader import Loader
from schemas.ingestion_schemas import IngestionRequest, IngestionResult


class IngestionService:
    def __init__(
        self, extractor: Extractor, transformer: Transformer, loader: Loader
    ):
        self._extractor = extractor
        self._transformer = transformer
        self._loader = loader

    async def run_ingestion(self, request: IngestionRequest) -> IngestionResult:
        stats = {"fetched": 0, "stored": 0, "skipped": 0, "errors": 0}

        for dataset_code in request.dataset_codes:
            cursor = None
            while True:
                raw_page = await self._extractor.fetch(
                    provider=request.provider,
                    dataset_code=dataset_code,
                    cursor=cursor,
                    period=request.period,
                )
                stats["fetched"] += len(raw_page.records)

                records = self._transformer.transform(
                    raw_page.records,
                    raw_page.columns,
                    dataset_code,
                    request.provider,
                )
                stats["errors"] += raw_page.record_count - len(records)

                count = self._loader.load(
                    records, dataset_code, request.provider, raw_page.columns
                )
                stats["stored"] += count

                cursor = raw_page.next_cursor
                if cursor is None:
                    break

        return IngestionResult(**stats)
