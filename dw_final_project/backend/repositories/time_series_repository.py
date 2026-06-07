from repositories.base_repository import BaseRepository
from models.time_series_model import TimeSeriesRecord
from config.constants import BATCH_SIZE
from datetime import date


class TimeSeriesRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self._stmt_save = self._prepare(
            "INSERT INTO data (asset_id, data_source_id, business_date_year, "
            "business_date, system_date, values_double, values_int, values_text, deleted) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        self._stmt_range = self._prepare(
            "SELECT * FROM data "
            "WHERE asset_id = ? AND data_source_id = ? AND business_date_year = ? "
            "AND business_date >= ? AND business_date < ?"
        )

    def save(self, record: TimeSeriesRecord) -> TimeSeriesRecord:
        self._execute(self._stmt_save, [
            record.asset_id, record.data_source_id, record.business_date_year,
            record.business_date, record.system_date,
            record.values_double, record.values_int, record.values_text,
            record.deleted,
        ])
        return record

    def save_batch(self, records: list[TimeSeriesRecord]) -> int:
        from cassandra.query import BatchStatement, BatchType

        total = 0
        # Chunk records to avoid oversized Cassandra batches
        for i in range(0, len(records), BATCH_SIZE):
            chunk = records[i : i + BATCH_SIZE]
            batch = BatchStatement(batch_type=BatchType.UNLOGGED)
            for r in chunk:
                batch.add(self._stmt_save, [
                    r.asset_id, r.data_source_id, r.business_date_year,
                    r.business_date, r.system_date,
                    r.values_double, r.values_int, r.values_text, r.deleted,
                ])
            self._execute(batch)
            total += len(chunk)
        return total

    def find_by_range(
        self,
        asset_id: str,
        data_source_id: str,
        start_date: date,
        end_date: date,
    ) -> list[TimeSeriesRecord]:
        results = []
        for year in range(start_date.year, end_date.year + 1):
            rows = self._execute(self._stmt_range, [
                asset_id, data_source_id, year, start_date, end_date,
            ])
            results.extend(self._to_model(r) for r in rows)

        latest_by_date: dict[date, TimeSeriesRecord] = {}
        for rec in results:
            existing = latest_by_date.get(rec.business_date)
            if existing is None or rec.system_date > existing.system_date:
                latest_by_date[rec.business_date] = rec

        return sorted(
            [r for r in latest_by_date.values() if not r.deleted],
            key=lambda r: r.business_date,
            reverse=True,
        )

    def _to_model(self, row) -> TimeSeriesRecord:
        return TimeSeriesRecord(
            asset_id=row.asset_id,
            data_source_id=row.data_source_id,
            business_date_year=row.business_date_year,
            business_date=row.business_date,
            system_date=row.system_date,
            values_double=dict(row.values_double) if row.values_double else {},
            values_int=dict(row.values_int) if row.values_int else {},
            values_text=dict(row.values_text) if row.values_text else {},
            deleted=row.deleted or False,
        )
