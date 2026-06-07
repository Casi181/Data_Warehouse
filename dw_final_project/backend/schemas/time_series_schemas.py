from pydantic import BaseModel


class TimeSeriesRecordSchema(BaseModel):
    businessDate: str
    values: dict[str, float | int | str]


class TimeSeriesDataResponse(BaseModel):
    data: dict
    attributes: list[str] | None = None
