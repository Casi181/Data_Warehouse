from fastapi import APIRouter, Depends
from schemas.analytics_schemas import (
    AggregateRequest,
    PredictRequest,
    SparkJobResult,
    TotalsResponse,
    PredictionResponse,
)
from services.analytics_service import AnalyticsService
from repositories.analytics_repository import TotalsRepository, RegressionRepository

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()


def get_totals_repo() -> TotalsRepository:
    return TotalsRepository()


def get_regression_repo() -> RegressionRepository:
    return RegressionRepository()


@router.post("/aggregate", response_model=SparkJobResult)
def run_aggregation(
    request: AggregateRequest,
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.run_aggregation(request.data_source_id)


@router.post("/predict", response_model=SparkJobResult)
def run_prediction(
    request: PredictRequest,
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.run_prediction(request.asset_id, request.data_source_id)


@router.get("/totals", response_model=list[TotalsResponse])
def get_totals(repo: TotalsRepository = Depends(get_totals_repo)):
    records = repo.find_all()
    return [
        TotalsResponse(
            asset_id=r.asset_id,
            business_date_year=r.business_date_year,
            cnt=r.cnt,
        )
        for r in records
    ]


@router.get("/predictions", response_model=list[PredictionResponse])
def get_predictions(repo: RegressionRepository = Depends(get_regression_repo)):
    records = repo.find_all_results()
    return [
        PredictionResponse(
            seconds=r.seconds, open=r.open, prediction=r.prediction
        )
        for r in records
    ]
