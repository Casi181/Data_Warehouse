from fastapi import APIRouter, Depends
from schemas.ingestion_schemas import IngestionRequest, IngestionResult
from services.ingestion_service import IngestionService
from etl.extractor import Extractor
from etl.transformer import Transformer
from etl.loader import Loader
from repositories.asset_repository import AssetRepository
from repositories.data_source_repository import DataSourceRepository
from repositories.time_series_repository import TimeSeriesRepository

router = APIRouter(prefix="/api/v1/ingest", tags=["Ingestion"])


def get_ingestion_service() -> IngestionService:
    extractor = Extractor()
    transformer = Transformer()
    loader = Loader(
        asset_repo=AssetRepository(),
        ds_repo=DataSourceRepository(),
        ts_repo=TimeSeriesRepository(),
    )
    return IngestionService(extractor, transformer, loader)


@router.post("", response_model=IngestionResult)
async def trigger_ingestion(
    request: IngestionRequest,
    service: IngestionService = Depends(get_ingestion_service),
):
    return await service.run_ingestion(request)
