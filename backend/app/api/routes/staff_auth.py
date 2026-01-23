"""Staff authentication endpoints.

Handles staff login and token refresh with role/gym_id claims in JWT.
Per ARCH-10: Custom JWT (FastAPI native) for authentication.
Per ARCH-12: JWT access + refresh rotation.
Per ARCH-13: Role claims in JWT for RBAC.
"""

from datetime import timedelta

import jwt
from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError
from sqlmodel import select

from app.api.deps import SessionDep
from app.core import security
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    needs_rehash,
    verify_password,
)
from app.models import (
    ForgotPasswordRequest,
    Message,
    NewPassword,
    RefreshTokenRequest,
    TokenPayload,
)
from app.models.staff import Staff, StaffLoginRequest, StaffToken
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter(prefix="/auth/staff", tags=["staff-auth"])


@router.post("/login", response_model=StaffToken)
def login_staff(
    session: SessionDep,
    login_data: StaffLoginRequest,
) -> StaffToken:
    """Authenticate staff member and return tokens with role/gym claims.

    Returns JWT tokens with:
    - role: Staff role (owner, manager, front_desk, instructor)
    - gym_id: Tenant identifier for multi-tenancy

    Security:
    - Same error for invalid email/password/inactive (no enumeration)
    - Tokens include type claim for validation
    """
    staff = session.exec(select(Staff).where(Staff.email == login_data.email)).first()

    # Same error for invalid email or password (prevent enumeration)
    if not staff or not staff.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
                "details": {},
            },
        )

    if not verify_password(login_data.password, staff.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
                "details": {},
            },
        )

    # Check if staff is active (AC #5) - same error, no enumeration
    if not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
                "details": {},
            },
        )

    # Upgrade legacy bcrypt hash if needed
    if needs_rehash(staff.hashed_password):
        staff.hashed_password = get_password_hash(login_data.password)
        session.add(staff)
        session.commit()

    # Generate tokens with role and gym_id claims (AC #1, #2)
    # Include token_version for rotation (ARCH-12)
    access_token = create_access_token(
        subject=str(staff.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        role=staff.role.value,
        gym_id=str(staff.gym_id),
    )
    refresh_token = create_refresh_token(
        subject=str(staff.id),
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        role=staff.role.value,
        gym_id=str(staff.gym_id),
        token_version=staff.token_version,
    )

    return StaffToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        role=staff.role.value,
        gym_id=str(staff.gym_id),
    )


@router.post("/refresh", response_model=StaffToken)
def refresh_staff_token(
    session: SessionDep,
    refresh_data: RefreshTokenRequest,
) -> StaffToken:
    """Refresh staff access token using refresh token (ARCH-12).

    Validates the refresh token and issues a new access + refresh token pair.
    Token version is validated and incremented to invalidate old refresh tokens.
    Role and gym_id claims are preserved in the new tokens.

    Args:
        session: Database session
        refresh_data: Contains the refresh token

    Returns:
        StaffToken with new tokens and preserved role/gym_id

    Raises:
        HTTPException: 401 INVALID_TOKEN if refresh token is invalid/expired/replayed
    """
    try:
        payload = jwt.decode(
            refresh_data.refresh_token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired refresh token",
                "details": {},
            },
        )

    # Verify token type is "refresh"
    if token_data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired refresh token",
                "details": {},
            },
        )

    # Get staff from token subject
    staff = session.get(Staff, token_data.sub)

    # Return same error for missing/inactive staff (no enumeration)
    if not staff or not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired refresh token",
                "details": {},
            },
        )

    # Validate token version for rotation (reject replayed tokens)
    if token_data.token_version != staff.token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired refresh token",
                "details": {},
            },
        )

    # Increment token version to invalidate old refresh tokens
    staff.token_version += 1
    session.add(staff)
    session.commit()
    session.refresh(staff)

    # Generate new token pair with new version and preserved claims
    access_token = create_access_token(
        subject=str(staff.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        role=staff.role.value,
        gym_id=str(staff.gym_id),
    )
    refresh_token = create_refresh_token(
        subject=str(staff.id),
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        role=staff.role.value,
        gym_id=str(staff.gym_id),
        token_version=staff.token_version,
    )

    return StaffToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        role=staff.role.value,
        gym_id=str(staff.gym_id),
    )


@router.post("/forgot-password")
def forgot_password(
    session: SessionDep,
    request_data: ForgotPasswordRequest,
) -> Message:
    """Request password reset email for staff (Story 1.5, AC #1, #5).

    Always returns success, regardless of whether email exists.
    Only sends email if staff exists and is active.
    This prevents email enumeration attacks.

    Args:
        session: Database session
        request_data: Contains the email address

    Returns:
        Message confirming request received (always success)
    """
    staff = session.exec(select(Staff).where(Staff.email == request_data.email)).first()

    # Only send email if staff exists and is active
    # But ALWAYS return success to prevent enumeration
    if staff and staff.is_active:
        if settings.emails_enabled:
            token = generate_password_reset_token(request_data.email, account_type="staff")
            email_data = generate_reset_password_email(
                email_to=staff.email,
                email=request_data.email,
                token=token,
            )
            send_email(
                email_to=staff.email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )

    return Message(message="If the email exists, a password reset link has been sent")


@router.post("/reset-password")
def reset_password(
    session: SessionDep,
    request_data: NewPassword,
) -> Message:
    """Reset staff password using token from email (Story 1.5, AC #2, #3, #4).

    Validates token, updates password, and invalidates all existing sessions
    by incrementing token_version.

    Args:
        session: Database session
        request_data: Contains the token and new password

    Returns:
        Message confirming password was reset

    Raises:
        HTTPException: 400 INVALID_TOKEN if token is invalid/expired
    """
    email = verify_password_reset_token(request_data.token, expected_account_type="staff")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired reset token",
                "details": {},
            },
        )

    staff = session.exec(select(Staff).where(Staff.email == email)).first()

    # Use same error for not found/inactive to prevent enumeration
    if not staff or not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired reset token",
                "details": {},
            },
        )

    # Update password with Argon2 hash (ARCH-11)
    staff.hashed_password = get_password_hash(request_data.new_password)

    # CRITICAL: Invalidate all existing sessions (ARCH-12)
    staff.token_version += 1

    session.add(staff)
    session.commit()

    return Message(message="Password has been reset successfully")
