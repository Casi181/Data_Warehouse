from repositories.base_repository import BaseRepository
from models.asset_model import AssetModel
from datetime import datetime, UTC


class AssetRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self._stmt_save = self._prepare(
            "INSERT INTO asset (id, system_date, name, description, attributes) "
            "VALUES (?, ?, ?, ?, ?)"
        )
        self._stmt_latest = self._prepare(
            "SELECT * FROM asset WHERE id = ? LIMIT 1"
        )
        self._stmt_all_versions = self._prepare(
            "SELECT * FROM asset WHERE id = ?"
        )

    def save(self, model: AssetModel) -> AssetModel:
        self._execute(self._stmt_save, [
            model.id, model.system_date, model.name,
            model.description, model.attributes,
        ])
        return model

    def find_latest(self, asset_id: str) -> AssetModel | None:
        row = self._execute(self._stmt_latest, [asset_id]).one()
        return self._to_model(row) if row else None

    def find_all_versions(self, asset_id: str) -> list[AssetModel]:
        rows = self._execute(self._stmt_all_versions, [asset_id])
        return [self._to_model(r) for r in rows]

    def find_all_ids_paginated(
        self, offset: int = 0, limit: int = 20
    ) -> tuple[list[str], int]:
        rows = list(self._execute("SELECT DISTINCT id FROM asset"))
        all_ids = sorted(r.id for r in rows)
        total = len(all_ids)
        return all_ids[offset : offset + limit], total

    def soft_delete(self, asset_id: str) -> None:
        deleted = AssetModel(
            id=asset_id,
            system_date=datetime.now(UTC),
            attributes={"deleted": "true"},
        )
        self.save(deleted)

    def _to_model(self, row) -> AssetModel:
        return AssetModel(
            id=row.id,
            system_date=row.system_date,
            name=row.name or "",
            description=row.description or "",
            attributes=dict(row.attributes) if row.attributes else {},
        )
