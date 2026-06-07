from datetime import date
from repositories.time_series_repository import TimeSeriesRepository


class TimeSeriesService:
    def __init__(self, repo: TimeSeriesRepository):
        self._repo = repo

    def get_time_series(
        self,
        asset_id: str,
        data_source_id: str,
        start_date: date,
        end_date: date,
        include_attributes: bool = False,
    ) -> dict:
        records = self._repo.find_by_range(
            asset_id, data_source_id, start_date, end_date
        )

        formatted = []
        all_attrs = set()
        for r in records:
            values: dict[str, float | int | str] = {}
            values.update(r.values_double)
            values.update(r.values_int)
            values.update(r.values_text)
            all_attrs.update(values.keys())
            formatted.append({
                "businessDate": str(r.business_date),
                "values": values,
            })

        result: dict = {
            "data": {
                "assetId": asset_id,
                "datasourceId": data_source_id,
                "records": formatted,
            }
        }
        if include_attributes:
            result["attributes"] = sorted(all_attrs)
        return result
