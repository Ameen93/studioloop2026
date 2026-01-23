"""FastAPI dependencies for authentication and tenant context.

This module provides:
- Database session dependency
- JWT authentication dependencies
- Gym (tenant) context dependency for multi-tenancy
"""

from collections.abc import Generator
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import Gym, TokenPayload, User
from app.models.consumer import Consumer
from app.models.staff import Staff

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    # Validate token type is "access" (reject refresh tokens used as bearer)
    if token_data.type != "access":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_consumer(session: SessionDep, token: TokenDep) -> Consumer:
    """Get the currently authenticated consumer from JWT token.

    Validates the access token and returns the Consumer if valid.
    Use this dependency for consumer-authenticated routes.

    Args:
        session: Database session
        token: JWT access token from Authorization header

    Returns:
        Consumer model instance

    Raises:
        HTTPException: 401 if token is invalid or consumer not found/inactive
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Could not validate credentials",
                "details": {},
            },
        )
    # Validate token type is "access" (reject refresh tokens)
    if token_data.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Could not validate credentials",
                "details": {},
            },
        )
    consumer = session.get(Consumer, token_data.sub)
    if not consumer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Could not validate credentials",
                "details": {},
            },
        )
    if not consumer.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Could not validate credentials",
                "details": {},
            },
        )
    return consumer


CurrentConsumer = Annotated[Consumer, Depends(get_current_consumer)]


def get_current_staff(session: SessionDep, token: TokenDep) -> Staff:
    """Get the currently authenticated staff member from JWT token.

    Validates the access token and returns the Staff if valid.
    Use this dependency for staff-authenticated routes.

    Args:
        session: Database session
        token: JWT access token from Authorization header

    Returns:
        Staff model instance

    Raises:
        HTTPException: 401 if token is invalid or staff not found/inactive
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Could not validate credentials",
                "details": {},
            },
        )
    # Validate token type is "access" (reject refresh tokens)
    if token_data.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Could not validate credentials",
                "details": {},
            },
        )
    staff = session.get(Staff, token_data.sub)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Could not validate credentials",
                "details": {},
            },
        )
    if not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Could not validate credentials",
                "details": {},
            },
        )
    return staff


CurrentStaff = Annotated[Staff, Depends(get_current_staff)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


# =============================================================================
# Gym (Tenant) Dependencies - Multi-Tenancy Support
# =============================================================================


def get_current_gym(
    gym_id: Annotated[UUID, Path(description="Gym ID (tenant identifier)")],
    session: SessionDep,
    _current_user: CurrentUser,  # Ensures user is authenticated; used for access validation in future
) -> Gym:
    """Get gym by ID with access validation.

    This dependency provides the tenant context for gym-scoped routes.
    It validates that:
    1. The gym exists
    2. The gym is active
    3. The user has access to this gym (TODO: implement role-based access)

    Usage in routes:
        @router.get("/gyms/{gym_id}/spaces")
        def list_spaces(gym: GymDep):
            # gym is now available with validated access
            ...

    Args:
        gym_id: UUID of the gym from path parameter
        session: Database session
        current_user: Authenticated user

    Returns:
        Gym model instance

    Raises:
        HTTPException: 404 if gym not found, 403 if access denied
    """
    gym = session.get(Gym, gym_id)
    if not gym:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gym not found",
        )
    if not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gym not found",  # Don't reveal soft-deleted status
        )

    # TODO: Implement user-gym access validation
    # This will check if the user has a role (staff, owner) at this gym
    # For now, all authenticated users can access any active gym
    # In future: check staff membership or gym ownership
    # if not has_gym_access(current_user, gym):
    #     raise HTTPException(status_code=403, detail="Access denied to this gym")

    return gym


# Annotated type for gym dependency injection
GymDep = Annotated[Gym, Depends(get_current_gym)]


def get_gym_id_from_path(
    gym_id: Annotated[UUID, Path(description="Gym ID (tenant identifier)")],
) -> UUID:
    """Get gym_id from path without loading the full Gym object.

    Use this when you only need the gym_id for filtering queries
    and don't need the full Gym model.

    Note: This does NOT validate that the gym exists. Use GymDep
    if you need existence/access validation.
    """
    return gym_id


GymIdDep = Annotated[UUID, Depends(get_gym_id_from_path)]


# =============================================================================
# Role-Based Access Control (RBAC) - Story 1.8
# =============================================================================

# Role hierarchy for permission inheritance (ARCH-13)
ROLE_HIERARCHY = {
    "owner": 4,
    "manager": 3,
    "front_desk": 2,
    "instructor": 2,  # Same level as front_desk (peer roles)
    "consumer": 1,
}


def has_permission(user_role: str, required_role: str) -> bool:
    """Check if user role has at least required permission level.

    Args:
        user_role: The role the user has
        required_role: The minimum role required

    Returns:
        True if user_role >= required_role in hierarchy
    """
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)


class RoleChecker:
    """FastAPI dependency for role-based access control (ARCH-13).

    Usage:
        @router.get("/admin", dependencies=[Depends(RoleChecker(["owner", "manager"]))])
        def admin_route(): ...

        # Or as a parameter dependency:
        @router.get("/admin")
        def admin_route(
            _role_check: Annotated[None, Depends(RoleChecker(["owner"]))]
        ): ...
    """

    def __init__(self, allowed_roles: list[str]):
        """Initialize RoleChecker with allowed roles.

        Args:
            allowed_roles: List of role names that are permitted access
        """
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        current_staff: CurrentStaff,
    ) -> None:
        """Check if current staff has required role.

        Args:
            current_staff: Authenticated staff from JWT

        Raises:
            HTTPException: 403 FORBIDDEN if role not allowed
        """
        if current_staff.role.value not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "Insufficient permissions",
                    "details": {"required_roles": self.allowed_roles},
                },
            )


# Convenience dependencies for common role requirements
RequireOwner = Depends(RoleChecker(["owner"]))
RequireOwnerOrManager = Depends(RoleChecker(["owner", "manager"]))
RequireManager = Depends(RoleChecker(["owner", "manager"]))  # Alias for clarity
RequireStaff = Depends(RoleChecker(["owner", "manager", "front_desk", "instructor"]))


def get_current_staff_for_gym(
    gym_id: Annotated[UUID, Path(description="Gym ID (tenant identifier)")],
    current_staff: CurrentStaff,
) -> Staff:
    """Validate staff member has access to the specified gym.

    Compares gym_id from path with staff's gym_id to ensure
    tenant isolation (multi-tenancy).

    Args:
        gym_id: UUID from path parameter
        current_staff: Authenticated staff from JWT

    Returns:
        Staff model if authorized

    Raises:
        HTTPException: 403 FORBIDDEN if gym_id mismatch
    """
    if str(current_staff.gym_id) != str(gym_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Access denied to this gym",
                "details": {},
            },
        )
    return current_staff


# Annotated type for gym-scoped staff dependency
StaffGymDep = Annotated[Staff, Depends(get_current_staff_for_gym)]
