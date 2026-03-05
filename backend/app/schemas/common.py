"""Common response schemas."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Wrapper for paginated list responses."""

    data: list[T]
    meta: dict


class ErrorResponse(BaseModel):
    """Standard error response shape."""

    detail: str
    code: str
