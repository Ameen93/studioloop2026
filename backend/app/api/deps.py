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
