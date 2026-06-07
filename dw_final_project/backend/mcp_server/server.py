from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp_server.tool_handlers import handle_tool_call
from mcp_server.validation import validate_inputs
import json

app = Server("casi-financial-dw")

TOOL_DEFINITIONS = [
    Tool(
        name="list_assets",
        description="Returns a paginated list of financial asset IDs in the warehouse. Use for discovery.",
        inputSchema={
            "type": "object",
            "properties": {
                "offset": {
                    "type": "integer",
                    "default": 0,
                    "description": "Start position (0-based)",
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Max results (1-100)",
                },
            },
        },
    ),
    Tool(
        name="get_asset_details",
        description="Returns all temporal versions of a specific asset (latest first). Use after finding an ID via list_assets.",
        inputSchema={
            "type": "object",
            "properties": {
                "assetId": {
                    "type": "string",
                    "description": "Asset identifier",
                }
            },
            "required": ["assetId"],
        },
    ),
    Tool(
        name="list_data_sources",
        description="Returns a paginated list of data source/provider IDs.",
        inputSchema={
            "type": "object",
            "properties": {
                "offset": {"type": "integer", "default": 0},
                "limit": {"type": "integer", "default": 20},
            },
        },
    ),
    Tool(
        name="get_data_source_details",
        description="Returns details of a specific data source including its supported attributes.",
        inputSchema={
            "type": "object",
            "properties": {
                "dataSourceId": {"type": "string"}
            },
            "required": ["dataSourceId"],
        },
    ),
    Tool(
        name="get_time_series_data",
        description=(
            "Returns time-series records for a given asset and data source "
            "within a bounded date range (max 365 days). Records returned "
            "newest-first, only latest version per business date. "
            "Set includeAttributes=true to see attribute names."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "assetId": {"type": "string"},
                "dataSourceId": {"type": "string"},
                "startBusinessDate": {
                    "type": "string",
                    "description": "YYYY-MM-DD",
                },
                "endBusinessDate": {
                    "type": "string",
                    "description": "YYYY-MM-DD",
                },
                "includeAttributes": {
                    "type": "boolean",
                    "default": False,
                },
            },
            "required": [
                "assetId",
                "dataSourceId",
                "startBusinessDate",
                "endBusinessDate",
            ],
        },
    ),
]


@app.list_tools()
async def list_tools():
    return TOOL_DEFINITIONS


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    validated = validate_inputs(name, arguments)
    result = await handle_tool_call(name, validated)
    return [TextContent(type="text", text=json.dumps(result, default=str))]


if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server

    async def main():
        from database.connection import init_cassandra
        from database.init_schema import create_tables

        init_cassandra()
        create_tables()

        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    asyncio.run(main())
