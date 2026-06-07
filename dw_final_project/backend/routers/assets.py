from fastapi import APIRouter, Depends, Query, HTTPException
from services.asset_service import AssetService
from repositories.asset_repository import AssetRepository

router = APIRouter(prefix="/api/v1/assets", tags=["Assets"])


def get_asset_service() -> AssetService:
    return AssetService(repo=AssetRepository())


@router.get("")
def list_assets(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: AssetService = Depends(get_asset_service),
):
    return service.list_assets(offset, limit)


@router.get("/{asset_id:path}")
def get_asset(
    asset_id: str,
    service: AssetService = Depends(get_asset_service),
):
    details = service.get_asset_details(asset_id)
    if not details:
        raise HTTPException(404, f"Asset '{asset_id}' not found")
    return details
