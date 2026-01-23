"""Custom exceptions for StudioLoop application.

This module defines custom exception classes that map to HTTP status codes
and provide consistent error responses across the API.

Usage:
    from app.core.exceptions import NotFoundError, ValidationError

    # In a route or service
    raise NotFoundError(resource="Space", id=space_id)
    raise ValidationError(message="Email already registered")
"""

from typing import Any
from uuid import UUID


class StudioLoopError(Exception):
    """Base exception for all StudioLoop application errors.

    All custom exceptions inherit from this class, allowing
    catch-all exception handling when needed.
    """

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        """Initialize the exception.

        Args:
            message: Human-readable error message
            code: Machine-readable error code (e.g., "RESOURCE_NOT_FOUND")
            details: Additional error context
        """
        self.message = message
        self.code = code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(message)


class NotFoundError(StudioLoopError):
    """Resource not found error - maps to HTTP 404.

    Use when a requested resource does not exist or the user
    doesn't have access to view it.
    """

    def __init__(
        self,
        resource: str,
        id: UUID | str | None = None,
        message: str | None = None,
    ):
        """Initialize not found error.

        Args:
            resource: Name of the resource type (e.g., "Space", "Gym")
            id: Optional ID of the resource that wasn't found
            message: Optional custom message (auto-generated if not provided)
        """
        if message is None:
            if id:
                message = f"{resource} with ID '{id}' not found"
            else:
                message = f"{resource} not found"

        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "id": str(id) if id else None},
        )


class ValidationError(StudioLoopError):
    """Validation error - maps to HTTP 422.

    Use when request data fails business logic validation
    (not schema validation, which is handled by Pydantic).
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        """Initialize validation error.

        Args:
            message: Description of the validation failure
            field: Optional field name that failed validation
            details: Additional validation context
        """
        error_details = details or {}
        if field:
            error_details["field"] = field

        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=error_details,
        )


class ConflictError(StudioLoopError):
    """Conflict error - maps to HTTP 409.

    Use when the request conflicts with current resource state,
    such as duplicate unique values or version conflicts.
    """

    def __init__(
        self,
        message: str,
        resource: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        """Initialize conflict error.

        Args:
            message: Description of the conflict
            resource: Optional resource type involved
            details: Additional conflict context
        """
        error_details = details or {}
        if resource:
            error_details["resource"] = resource

        super().__init__(
            message=message,
            code="CONFLICT",
            details=error_details,
        )


class PermissionDeniedError(StudioLoopError):
    """Permission denied error - maps to HTTP 403.

    Use when the user is authenticated but doesn't have
    permission to perform the requested action.
    """

    def __init__(
        self,
        message: str = "Permission denied",
        action: str | None = None,
        resource: str | None = None,
    ):
        """Initialize permission denied error.

        Args:
            message: Custom message (default: "Permission denied")
            action: Optional action that was attempted
            resource: Optional resource type involved
        """
        details: dict[str, Any] = {}
        if action:
            details["action"] = action
        if resource:
            details["resource"] = resource

        super().__init__(
            message=message,
            code="PERMISSION_DENIED",
            details=details,
        )


class TenantAccessError(PermissionDeniedError):
    """Cross-tenant access attempt - maps to HTTP 403.

    Use when a user attempts to access resources belonging
    to a different gym/tenant.

    SECURITY: This is critical for multi-tenancy isolation.
    """

    def __init__(
        self,
        message: str = "Access denied to this gym",
        gym_id: UUID | None = None,
    ):
        """Initialize tenant access error.

        Args:
            message: Custom message
            gym_id: Optional gym ID that was attempted to access
        """
        super().__init__(
            message=message,
            action="cross_tenant_access",
            resource="gym",
        )
        if gym_id:
            self.details["gym_id"] = str(gym_id)
        self.code = "TENANT_ACCESS_DENIED"


class BusinessRuleError(StudioLoopError):
    """Business rule violation - maps to HTTP 400.

    Use when a request violates business logic rules,
    such as booking a class that's full.
    """

    def __init__(
        self,
        message: str,
        rule: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        """Initialize business rule error.

        Args:
            message: Description of the rule violation
            rule: Optional identifier for the business rule
            details: Additional context
        """
        error_details = details or {}
        if rule:
            error_details["rule"] = rule

        super().__init__(
            message=message,
            code="BUSINESS_RULE_VIOLATION",
            details=error_details,
        )
