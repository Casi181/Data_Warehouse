from repositories.base_repository import BaseRepository
from models.data_source_model import DataSourceModel


class DataSourceRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self._stmt_save = self._prepare(
            "INSERT INTO data_source (id, system_date, name, description, attributes) "
            "VALUES (?, ?, ?, ?, ?)"
        )
        self._stmt_latest = self._prepare(
            "SELECT * FROM data_source WHERE id = ? LIMIT 1"
        )
        self._stmt_all_versions = self._prepare(
            "SELECT * FROM data_source WHERE id = ?"
        )

    def save(self, model: DataSourceModel) -> DataSourceModel:
        self._execute(self._stmt_save, [
            model.id, model.system_date, model.name,
            model.description, model.attributes,
        ])
        return model

    def find_latest(self, ds_id: str) -> DataSourceModel | None:
        row = self._execute(self._stmt_latest, [ds_id]).one()
        return self._to_model(row) if row else None

    def find_all_versions(self, ds_id: str) -> list[DataSourceModel]:
        rows = self._execute(self._stmt_all_versions, [ds_id])
        return [self._to_model(r) for r in rows]

    def find_all_ids_paginated(
        self, offset: int = 0, limit: int = 20
    ) -> tuple[list[str], int]:
        rows = list(self._execute("SELECT DISTINCT id FROM data_source"))
        all_ids = sorted(r.id for r in rows)
        total = len(all_ids)
        return all_ids[offset : offset + limit], total

    def _to_model(self, row) -> DataSourceModel:
        return DataSourceModel(
            id=row.id,
            system_date=row.system_date,
            name=row.name or "",
            description=row.description or "",
            attributes=set(row.attributes) if row.attributes else set(),
        )
