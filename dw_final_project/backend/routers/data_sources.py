from fastapi import APIRouter, Depends, Query, HTTPException
from services.data_source_service import DataSourceService
from repositories.data_source_repository import DataSourceRepository

router = APIRouter(prefix="/api/v1/data-sources", tags=["Data Sources"])


def get_ds_service() -> DataSourceService:
    return DataSourceService(repo=DataSourceRepository())


@router.get("")
def list_data_sources(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: DataSourceService = Depends(get_ds_service),
):
    return service.list_data_sources(offset, limit)


@router.get("/{data_source_id:path}")
def get_data_source(
    data_source_id: str,
    service: DataSourceService = Depends(get_ds_service),
):
    details = service.get_details(data_source_id)
    if not details:
        raise HTTPException(404, f"Data source '{data_source_id}' not found")
    return details
