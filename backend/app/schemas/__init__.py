"""API schemas for request/response validation.

This package contains Pydantic schemas for API data validation.
"""

from app.schemas.common import (
    DeleteResponse,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
    SuccessResponse,
    ERROR_RESPONSES,
)

__all__ = [
    "DeleteResponse",
    "ErrorDetail",
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationMeta",
    "SuccessResponse",
    "ERROR_RESPONSES",
]
