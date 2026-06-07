from services.asset_service import AssetService
from services.data_source_service import DataSourceService
from services.time_series_service import TimeSeriesService
from repositories.asset_repository import AssetRepository
from repositories.data_source_repository import DataSourceRepository
from repositories.time_series_repository import TimeSeriesRepository
from datetime import date

_asset_svc = None
_ds_svc = None
_ts_svc = None


def _get_services():
    global _asset_svc, _ds_svc, _ts_svc
    if _asset_svc is None:
        _asset_svc = AssetService(AssetRepository())
        _ds_svc = DataSourceService(DataSourceRepository())
        _ts_svc = TimeSeriesService(TimeSeriesRepository())
    return _asset_svc, _ds_svc, _ts_svc


async def handle_tool_call(name: str, args: dict) -> dict | list:
    asset_svc, ds_svc, ts_svc = _get_services()

    if name == "list_assets":
        result = asset_svc.list_assets(
            args.get("offset", 0), args.get("limit", 20)
        )
        return result.model_dump()

    elif name == "get_asset_details":
        details = asset_svc.get_asset_details(args["assetId"])
        if not details:
            return {
                "error": "not_found",
                "detail": f"Asset '{args['assetId']}' not found",
            }
        return [d.model_dump() for d in details]

    elif name == "list_data_sources":
        result = ds_svc.list_data_sources(
            args.get("offset", 0), args.get("limit", 20)
        )
        return result.model_dump()

    elif name == "get_data_source_details":
        details = ds_svc.get_details(args["dataSourceId"])
        if not details:
            return {
                "error": "not_found",
                "detail": f"Data source '{args['dataSourceId']}' not found",
            }
        return [d.model_dump() for d in details]

    elif name == "get_time_series_data":
        start = date.fromisoformat(args["startBusinessDate"])
        end = date.fromisoformat(args["endBusinessDate"])
        return ts_svc.get_time_series(
            args["assetId"],
            args["dataSourceId"],
            start,
            end,
            args.get("includeAttributes", False),
        )

    else:
        return {"error": "unknown_tool", "detail": f"Tool '{name}' not found"}
