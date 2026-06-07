from models.time_series_model import TimeSeriesRecord
from datetime import date, datetime, UTC
import logging

logger = logging.getLogger(__name__)


class Transformer:
    def transform(
        self,
        raw_records: list[dict],
        columns: list[str],
        dataset_code: str,
        provider: str,
    ) -> list[TimeSeriesRecord]:
        results = []
        for raw in raw_records:
            try:
                bdate = date.fromisoformat(
                    str(raw.get("date", raw.get("Date", "")))
                )
                vals_double: dict[str, float] = {}
                vals_text: dict[str, str] = {}
                for col in columns:
                    if col.lower() == "date":
                        continue
                    val = raw.get(col)
                    if val is None:
                        continue
                    try:
                        vals_double[col] = float(val)
                    except (ValueError, TypeError):
                        vals_text[col] = str(val)

                results.append(
                    TimeSeriesRecord(
                        asset_id=dataset_code,
                        data_source_id=provider,
                        business_date_year=bdate.year,
                        business_date=bdate,
                        system_date=datetime.now(UTC),
                        values_double=vals_double,
                        values_text=vals_text,
                    )
                )
            except Exception as exc:
                logger.debug(
                    "Skipping record in %s/%s: %s", provider, dataset_code, exc
                )
                continue
        return results
