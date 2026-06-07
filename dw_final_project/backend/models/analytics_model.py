from dataclasses import dataclass
from datetime import date


@dataclass
class TotalsRecord:
    asset_id: str
    business_date_year: int
    cnt: int


@dataclass
class RegressionDataRecord:
    bdate: date
    seconds: int
    open: float
    close: float
    low: float
    high: float


@dataclass
class RegressionResultRecord:
    seconds: int
    open: float
    prediction: float
