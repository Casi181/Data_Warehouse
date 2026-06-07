from pydantic import BaseModel
from typing import Any


class PaginatedResponse(BaseModel):
    items: list[Any]
    offset: int
    limit: int
    total: int
    has_next: bool


class ErrorDetail(BaseModel):
    error: str
    detail: str
