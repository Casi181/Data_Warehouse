from datetime import date


def validate_inputs(tool_name: str, arguments: dict) -> dict:
    validated = dict(arguments)

    if tool_name in ("list_assets", "list_data_sources"):
        offset = validated.get("offset", 0)
        limit = validated.get("limit", 20)
        if not isinstance(offset, int) or offset < 0:
            validated["offset"] = 0
        if not isinstance(limit, int) or limit < 1:
            validated["limit"] = 20
        if limit > 100:
            validated["limit"] = 100

    if tool_name == "get_time_series_data":
        start_str = validated.get("startBusinessDate", "")
        end_str = validated.get("endBusinessDate", "")
        try:
            start = date.fromisoformat(start_str)
            end = date.fromisoformat(end_str)
            if (end - start).days > 365:
                raise ValueError("Date range exceeds 365 days")
            if end <= start:
                raise ValueError("End date must be after start date")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid date parameters: {e}")

    return validated
