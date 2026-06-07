from fastapi import Request
from fastapi.responses import JSONResponse
from schemas.common_schemas import ErrorDetail
import logging

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorDetail(
            error="internal_server_error",
            detail="An unexpected error occurred. Check server logs for details.",
        ).model_dump(),
    )
