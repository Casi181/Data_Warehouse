from repositories.base_repository import BaseRepository
from models.analytics_model import TotalsRecord, RegressionResultRecord


class TotalsRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def find_all(self) -> list[TotalsRecord]:
        rows = self._execute("SELECT * FROM totals")
        return [
            TotalsRecord(
                asset_id=r.asset_id,
                business_date_year=r.business_date_year,
                cnt=r.cnt,
            )
            for r in rows
        ]

    def find_by_asset(self, asset_id: str) -> list[TotalsRecord]:
        rows = self._execute(
            "SELECT * FROM totals WHERE asset_id = ?", [asset_id]
        )
        return [
            TotalsRecord(
                asset_id=r.asset_id,
                business_date_year=r.business_date_year,
                cnt=r.cnt,
            )
            for r in rows
        ]


class RegressionRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def find_all_results(self) -> list[RegressionResultRecord]:
        rows = self._execute("SELECT * FROM regression_results")
        return [
            RegressionResultRecord(
                seconds=r.seconds, open=r.open, prediction=r.prediction
            )
            for r in rows
        ]
