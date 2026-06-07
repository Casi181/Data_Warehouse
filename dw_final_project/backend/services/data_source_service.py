from repositories.data_source_repository import DataSourceRepository
from schemas.data_source_schemas import DataSourceDetail
from schemas.common_schemas import PaginatedResponse


class DataSourceService:
    def __init__(self, repo: DataSourceRepository):
        self._repo = repo

    def list_data_sources(
        self, offset: int = 0, limit: int = 20
    ) -> PaginatedResponse:
        ids, total = self._repo.find_all_ids_paginated(offset, limit)
        return PaginatedResponse(
            items=ids,
            offset=offset,
            limit=limit,
            total=total,
            has_next=(offset + limit < total),
        )

    def get_details(self, ds_id: str) -> list[DataSourceDetail]:
        versions = self._repo.find_all_versions(ds_id)
        if not versions:
            return []
        return [DataSourceDetail.from_model(v) for v in versions]
