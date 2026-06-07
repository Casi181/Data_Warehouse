from pydantic import BaseModel
from typing import Any


class AggregateRequest(BaseModel):
    data_source_id: str


class PredictRequest(BaseModel):
    asset_id: str
    data_source_id: str


class SparkJobResult(BaseModel):
    status: str
    rows_processed: int = 0
    message: str = ""
    metrics: dict[str, Any] | None = None


class TotalsResponse(BaseModel):
    asset_id: str
    business_date_year: int
    cnt: int


class PredictionResponse(BaseModel):
    seconds: int
    open: float
    prediction: float
