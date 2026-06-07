from pydantic import BaseModel


class IngestionRequest(BaseModel):
    provider: str = "YFINANCE"
    dataset_codes: list[str]
    period: str = "1y"  # yfinance period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max


class IngestionResult(BaseModel):
    fetched: int = 0
    stored: int = 0
    skipped: int = 0
    errors: int = 0
