from fastapi import APIRouter
from pydantic import BaseModel
from mcp_server.tool_handlers import handle_tool_call
from datetime import date, timedelta
import re
import json

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


# Common ticker symbols for recognition
_TICKER_PATTERN = re.compile(
    r"\b([A-Z]{1,5}(?:-[A-Z]{1,4})?(?:/[A-Z]{3})?)\b"
)


def _extract_ticker(text: str) -> str | None:
    """Try to find a ticker symbol in the message."""
    matches = _TICKER_PATTERN.findall(text.upper())
    # Filter out common English words
    stopwords = {"I", "A", "IS", "IT", "THE", "AND", "OR", "TO", "IN", "OF", "FOR", "ON", "AT", "BY", "DO", "IF", "SO", "NO", "UP", "AN", "AS", "AM", "BE", "HE", "ME", "WE", "US", "MY"}
    for m in matches:
        if m not in stopwords and len(m) >= 2:
            return m
    return None


def _format_price_data(records: list[dict], ticker: str) -> str:
    """Format time series records into a readable summary."""
    if not records:
        return f"No recent data found for {ticker}."

    latest = records[0] if records else {}
    values = latest.get("values", {})
    bdate = latest.get("businessDate", "unknown")

    parts = [f"**{ticker}** (as of {bdate}):"]
    if "Close" in values:
        parts.append(f"- Close: ${float(values['Close']):.2f}")
    if "Open" in values:
        parts.append(f"- Open: ${float(values['Open']):.2f}")
    if "High" in values:
        parts.append(f"- High: ${float(values['High']):.2f}")
    if "Low" in values:
        parts.append(f"- Low: ${float(values['Low']):.2f}")
    if "Volume" in values:
        parts.append(f"- Volume: {int(float(values['Volume'])):,}")

    if len(records) > 1:
        prev = records[1].get("values", {})
        if "Close" in prev and "Close" in values:
            change = float(values["Close"]) - float(prev["Close"])
            pct = (change / float(prev["Close"])) * 100 if float(prev["Close"]) else 0
            direction = "up" if change >= 0 else "down"
            parts.append(f"- Daily change: {direction} ${abs(change):.2f} ({pct:+.2f}%)")

    return "\n".join(parts)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    text = request.message.strip()
    lower = text.lower()

    # Route: list assets
    if any(kw in lower for kw in ["list assets", "what assets", "which assets", "show assets", "all assets", "available assets", "tickers", "symbols"]):
        result = await handle_tool_call("list_assets", {"offset": 0, "limit": 50})
        items = result.get("items", [])
        if items:
            return ChatResponse(
                reply=f"I found {result.get('total', len(items))} assets in the warehouse. Here are some:\n\n{', '.join(items[:30])}"
                + ("\n\n...and more." if len(items) > 30 else "")
            )
        return ChatResponse(reply="No assets found in the warehouse yet. Data may still be loading — try again in a moment.")

    # Route: list data sources
    if any(kw in lower for kw in ["data source", "providers", "sources"]):
        result = await handle_tool_call("list_data_sources", {"offset": 0, "limit": 20})
        items = result.get("items", [])
        if items:
            return ChatResponse(reply=f"Available data sources: {', '.join(items)}")
        return ChatResponse(reply="No data sources registered yet. Run an ingestion first.")

    # Route: price / quote / data for a specific ticker
    ticker = _extract_ticker(text)
    if ticker and any(kw in lower for kw in ["price", "quote", "data", "show", "get", "how", "what", "close", "open", "value", "worth"]):
        end = date.today()
        start = end - timedelta(days=10)
        try:
            result = await handle_tool_call("get_time_series_data", {
                "assetId": ticker,
                "dataSourceId": "YFINANCE",
                "startBusinessDate": start.isoformat(),
                "endBusinessDate": end.isoformat(),
            })
            data = result.get("data", {}) if isinstance(result, dict) else {}
            records = data.get("records", []) if isinstance(data, dict) else []
            return ChatResponse(reply=_format_price_data(records, ticker))
        except Exception:
            return ChatResponse(reply=f"Could not fetch data for {ticker}. It may not be in the warehouse.")

    # Route: asset details
    if ticker and any(kw in lower for kw in ["detail", "info", "about", "tell me"]):
        result = await handle_tool_call("get_asset_details", {"assetId": ticker})
        if isinstance(result, list) and result:
            r = result[0]
            attrs = r.get("attributes", {})
            return ChatResponse(
                reply=f"**{r.get('name', ticker)}** ({r.get('id', ticker)})\n"
                f"- Description: {r.get('description', 'N/A')}\n"
                f"- Class: {attrs.get('class', 'unknown')}\n"
                f"- Exchange: {attrs.get('exchange', 'unknown')}\n"
                f"- Region: {attrs.get('region', 'unknown')}"
            )
        return ChatResponse(reply=f"No details found for '{ticker}'.")

    # Route: if we detect a ticker but no specific keyword, show price
    if ticker:
        end = date.today()
        start = end - timedelta(days=10)
        try:
            result = await handle_tool_call("get_time_series_data", {
                "assetId": ticker,
                "dataSourceId": "YFINANCE",
                "startBusinessDate": start.isoformat(),
                "endBusinessDate": end.isoformat(),
            })
            data = result.get("data", {}) if isinstance(result, dict) else {}
            records = data.get("records", []) if isinstance(data, dict) else []
            if records:
                return ChatResponse(reply=_format_price_data(records, ticker))
        except Exception:
            pass

    # Default: help message
    return ChatResponse(
        reply="I can help you with:\n\n"
        "- **List assets** — \"What assets are available?\"\n"
        "- **Asset price** — \"What's the price of AAPL?\"\n"
        "- **Asset details** — \"Tell me about MSFT\"\n"
        "- **Data sources** — \"What data sources are there?\"\n\n"
        "Try asking about a specific ticker symbol!"
    )
