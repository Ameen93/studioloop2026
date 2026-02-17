"""FastAPI exception handlers for custom exceptions.

This module registers exception handlers with the FastAPI application
to convert custom exceptions into standard error responses.

Usage:
    from app.core.exception_handlers import register_exception_handlers

    app = FastAPI()
    register_exception_handlers(app)
"""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    BusinessRuleError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    StudioLoopError,
    TenantAccessError,
    ValidationError,
)


def _create_error_response(
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """Create a standard error response.

    Args:
        status_code: HTTP status code
        code: Machine-readable error code
        message: Human-readable error message
        details: Additional error context

    Returns:
        JSONResponse with standard error format
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


async def not_found_error_handler(
    _request: Request,
    exc: NotFoundError,
) -> JSONResponse:
    """Handle NotFoundError exceptions."""
    return _create_error_response(
        status_code=404,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def validation_error_handler(
    _request: Request,
    exc: ValidationError,
) -> JSONResponse:
    """Handle ValidationError exceptions."""
    return _create_error_response(
        status_code=422,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def conflict_error_handler(
    _request: Request,
    exc: ConflictError,
) -> JSONResponse:
    """Handle ConflictError exceptions."""
    return _create_error_response(
        status_code=409,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def permission_denied_error_handler(
    _request: Request,
    exc: PermissionDeniedError,
) -> JSONResponse:
    """Handle PermissionDeniedError exceptions."""
    return _create_error_response(
        status_code=403,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def tenant_access_error_handler(
    _request: Request,
    exc: TenantAccessError,
) -> JSONResponse:
    """Handle TenantAccessError exceptions.

    SECURITY: Uses same response as PermissionDeniedError to avoid
    leaking information about tenant existence.
    """
    return _create_error_response(
        status_code=403,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def business_rule_error_handler(
    _request: Request,
    exc: BusinessRuleError,
) -> JSONResponse:
    """Handle BusinessRuleError exceptions."""
    return _create_error_response(
        status_code=400,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def studioloop_error_handler(
    _request: Request,
    exc: StudioLoopError,
) -> JSONResponse:
    """Catch-all handler for any StudioLoopError not handled above."""
    return _create_error_response(
        status_code=500,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers with the FastAPI app.

    Args:
        app: FastAPI application instance

    Example:
        app = FastAPI()
        register_exception_handlers(app)
    """
    # Register specific handlers first (more specific exceptions)
    # Note: type: ignore needed because FastAPI expects Callable[[Request, Exception], ...]
    # but we use typed exception handlers for better type safety within handlers
    app.add_exception_handler(TenantAccessError, tenant_access_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(PermissionDeniedError, permission_denied_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(NotFoundError, not_found_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ConflictError, conflict_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(BusinessRuleError, business_rule_error_handler)  # type: ignore[arg-type]

    # Register base handler last (catch-all for any unhandled StudioLoopError)
    app.add_exception_handler(StudioLoopError, studioloop_error_handler)  # type: ignore[arg-type]
