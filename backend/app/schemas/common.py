"""Common schemas used across the API.

This module provides standard response schemas for consistent API responses.
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

# Generic type for paginated data
DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    """Standard error detail schema.

    Used in error responses to provide structured error information.
    """

    code: str = Field(
        description="Machine-readable error code (e.g., 'RESOURCE_NOT_FOUND')"
    )
    message: str = Field(description="Human-readable error message")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional error context and metadata",
    )


class ErrorResponse(BaseModel):
    """Standard error response schema.

    All API errors should return this format for consistency.

    Example:
        {
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": "Space with ID 'abc-123' not found",
                "details": {"resource": "Space", "id": "abc-123"}
            }
        }
    """

    error: ErrorDetail


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""

    total: int = Field(ge=0, description="Total number of items available")
    skip: int = Field(ge=0, description="Number of items skipped")
    limit: int = Field(ge=1, description="Maximum items per page")
    has_more: bool = Field(description="Whether more items exist beyond this page")


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Standard paginated list response.

    Example:
        {
            "data": [...],
            "pagination": {
                "total": 150,
                "skip": 0,
                "limit": 20,
                "has_more": true
            }
        }
    """

    data: list[DataT]
    pagination: PaginationMeta


class SuccessResponse(BaseModel):
    """Simple success response for operations that don't return data."""

    success: bool = Field(default=True)
    message: str | None = Field(default=None, description="Optional success message")


class DeleteResponse(SuccessResponse):
    """Response for delete operations."""

    id: UUID = Field(description="ID of the deleted resource")


# Common response schema configurations for OpenAPI docs
ERROR_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Bad Request - Business rule violation"},
    403: {"model": ErrorResponse, "description": "Forbidden - Permission denied"},
    404: {"model": ErrorResponse, "description": "Not Found - Resource doesn't exist"},
    409: {"model": ErrorResponse, "description": "Conflict - Resource already exists"},
    422: {"model": ErrorResponse, "description": "Validation Error"},
}
