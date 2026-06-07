from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import date, timedelta
from services.time_series_service import TimeSeriesService
from repositories.time_series_repository import TimeSeriesRepository
from repositories.asset_repository import AssetRepository

router = APIRouter(prefix="/api/v1/data", tags=["Time Series"])


def get_ts_service() -> TimeSeriesService:
    return TimeSeriesService(repo=TimeSeriesRepository())


@router.get("/latest-prices")
def get_latest_prices(
    service: TimeSeriesService = Depends(get_ts_service),
):
    """Return latest close price + daily change for all assets (for dashboard ticker list)."""
    asset_repo = AssetRepository()
    asset_ids, _ = asset_repo.find_all_ids_paginated(limit=200)
    ts_repo = TimeSeriesRepository()

    today = date.today()
    start = today - timedelta(days=10)  # look back 10 days to find most recent trading day

    results = []
    for aid in asset_ids:
        # Try YFINANCE first, then BITFINEX
        for ds in ["YFINANCE", "BITFINEX"]:
            rows = ts_repo.find_by_range(aid, ds, start, today + timedelta(days=1))
            if rows:
                latest = rows[0]  # already sorted desc by date
                close = latest.values_double.get("Close", 0.0)
                prev_close = rows[1].values_double.get("Close", close) if len(rows) > 1 else close
                change = close - prev_close
                change_pct = (change / prev_close * 100) if prev_close else 0.0
                # Get asset metadata
                asset = asset_repo.find_latest(aid)
                results.append({
                    "id": aid,
                    "name": asset.name if asset else aid,
                    "asset_class": asset.attributes.get("class", "unknown") if asset else "unknown",
                    "region": asset.attributes.get("region", "") if asset else "",
                    "exchange": asset.attributes.get("exchange", "") if asset else "",
                    "provider": ds,
                    "close": round(close, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                    "date": str(latest.business_date),
                    "open": round(latest.values_double.get("Open", 0.0), 2),
                    "high": round(latest.values_double.get("High", 0.0), 2),
                    "low": round(latest.values_double.get("Low", 0.0), 2),
                    "volume": int(latest.values_double.get("Volume", 0)),
                })
                break
    return results


@router.get("")
def get_time_series(
    assetId: str = Query(...),
    dataSourceId: str = Query(...),
    startBusinessDate: date = Query(...),
    endBusinessDate: date = Query(...),
    includeAttributes: bool = Query(False),
    service: TimeSeriesService = Depends(get_ts_service),
):
    if (endBusinessDate - startBusinessDate).days > 1095:
        raise HTTPException(400, "Date range cannot exceed 3 years")
    if endBusinessDate <= startBusinessDate:
        raise HTTPException(400, "endBusinessDate must be after startBusinessDate")

    return service.get_time_series(
        assetId, dataSourceId, startBusinessDate,
        endBusinessDate, includeAttributes,
    )
