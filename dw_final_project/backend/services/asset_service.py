from repositories.asset_repository import AssetRepository
from schemas.asset_schemas import AssetDetail
from schemas.common_schemas import PaginatedResponse


class AssetService:
    def __init__(self, repo: AssetRepository):
        self._repo = repo

    def list_assets(self, offset: int = 0, limit: int = 20) -> PaginatedResponse:
        ids, total = self._repo.find_all_ids_paginated(offset, limit)
        return PaginatedResponse(
            items=ids,
            offset=offset,
            limit=limit,
            total=total,
            has_next=(offset + limit < total),
        )

    def get_asset_details(self, asset_id: str) -> list[AssetDetail]:
        versions = self._repo.find_all_versions(asset_id)
        if not versions:
            return []
        return [AssetDetail.from_model(v) for v in versions]
