"""Staff authentication endpoints.

Handles staff login, token refresh, and OAuth with role/gym_id claims in JWT.
Per ARCH-10: Custom JWT (FastAPI native) for authentication.
Per ARCH-12: JWT access + refresh rotation.
Per ARCH-13: Role claims in JWT for RBAC.
"""

from datetime import timedelta

import jwt
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import ValidationError
from sqlmodel import or_, select
from starlette.responses import Response

from app.api.deps import CurrentStaff, SessionDep
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
from app.models.staff import (
    Staff,
    StaffLoginRequest,
    StaffPublic,
    StaffToken,
    StaffUpdate,
)
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    validate_sa_phone,
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
        staff_id=str(staff.id),
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
        staff_id=str(staff.id),
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
            token = generate_password_reset_token(
                request_data.email, account_type="staff"
            )
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
    email = verify_password_reset_token(
        request_data.token, expected_account_type="staff"
    )

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


@router.get("/me", response_model=StaffPublic)
def get_current_staff_profile(
    current_staff: CurrentStaff,
) -> Staff:
    """Get current staff member's profile (Story 1.6, AC #5).

    Returns the authenticated staff member's profile information.
    Requires a valid access token.

    Args:
        current_staff: Authenticated staff from JWT token

    Returns:
        StaffPublic with profile data including role and gym_id
    """
    return current_staff


@router.patch("/me", response_model=StaffPublic)
def update_staff_profile(
    session: SessionDep,
    current_staff: CurrentStaff,
    update_data: StaffUpdate,
) -> Staff:
    """Update current staff member's profile (Story 1.6, AC #5).

    Allows partial updates - only provided fields are updated.
    Phone number must be in SA format (+27...) if provided.
    Role and gym_id cannot be changed via this endpoint.

    Args:
        session: Database session
        current_staff: Authenticated staff from JWT token
        update_data: Fields to update (first_name, last_name, phone)

    Returns:
        StaffPublic with updated profile data

    Raises:
        HTTPException: 400 INVALID_PHONE_FORMAT if phone format is invalid
    """
    # Validate phone if provided (not None and not empty string in update)
    update_dict = update_data.model_dump(exclude_unset=True)

    # Reject null for non-nullable fields
    non_nullable_fields = ["first_name", "last_name"]
    for field in non_nullable_fields:
        if field in update_dict and update_dict[field] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_FIELD_VALUE",
                    "message": f"{field} cannot be null",
                    "details": {"field": field},
                },
            )

    if "phone" in update_dict and update_dict["phone"] is not None:
        try:
            update_dict["phone"] = validate_sa_phone(update_dict["phone"])
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_PHONE_FORMAT",
                    "message": str(e),
                    "details": {"field": "phone"},
                },
            )

    # Update only provided fields
    for field, value in update_dict.items():
        setattr(current_staff, field, value)

    session.add(current_staff)
    session.commit()
    session.refresh(current_staff)

    return current_staff


# =============================================================================
# Staff Google OAuth Endpoints
# =============================================================================


def _build_staff_token(staff: Staff) -> StaffToken:
    """Build a StaffToken with JWT access and refresh tokens."""
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
        staff_id=str(staff.id),
        role=staff.role.value,
        gym_id=str(staff.gym_id),
    )


@router.get("/google")
async def staff_google_login(
    request: Request,
    redirect_uri: str | None = None,
) -> Response:
    """Initiate Google OAuth flow for staff.

    Args:
        request: FastAPI request object
        redirect_uri: Frontend URL to redirect to after OAuth completes
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "OAUTH_NOT_CONFIGURED",
                "message": "Google OAuth is not configured",
                "details": {},
            },
        )

    from app.core.oauth import oauth

    if redirect_uri:
        from app.core.oauth_utils import validate_oauth_redirect_uri

        validate_oauth_redirect_uri(redirect_uri)
        request.session["oauth_redirect_uri"] = redirect_uri

    google_redirect = settings.GOOGLE_STAFF_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, google_redirect)  # type: ignore[no-any-return]


@router.get("/google/callback", response_model=None)
async def staff_google_callback(
    request: Request,
    session: SessionDep,
) -> StaffToken | Response:
    """Handle Google OAuth callback for staff (link-only, no auto-creation).

    Staff must already exist (created by gym owner). This endpoint:
    - Finds staff by google_id or email
    - Links google_id if not already linked
    - Returns tokens with role/gym_id claims
    - Errors if no staff account found
    """
    from app.core.oauth import oauth
    from app.core.oauth_utils import build_oauth_redirect_response

    def _oauth_error(code: str, message: str, http_status: int = 400) -> Response:
        frontend_redirect = request.session.pop("oauth_redirect_uri", None)
        if frontend_redirect:
            return build_oauth_redirect_response(
                frontend_redirect, {"error": code, "error_message": message}
            )
        raise HTTPException(
            status_code=http_status,
            detail={"code": code, "message": message, "details": {}},
        )

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        return _oauth_error(
            "OAUTH_NOT_CONFIGURED", "Google OAuth is not configured", 503
        )

    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception:
        return _oauth_error("INVALID_OAUTH_STATE", "Invalid or expired OAuth state")

    user_info = token.get("userinfo")
    if not user_info:
        return _oauth_error(
            "OAUTH_USER_INFO_FAILED", "Failed to get user info from Google"
        )

    google_id = user_info.get("sub")
    email = user_info.get("email")

    if not email:
        return _oauth_error(
            "OAUTH_NO_EMAIL", "Google account does not have an email address"
        )

    # Find existing staff by google_id or email (link-only, no creation)
    staff = session.exec(
        select(Staff).where(or_(Staff.google_id == google_id, Staff.email == email))
    ).first()

    if not staff or not staff.is_active:
        return _oauth_error(
            "NO_STAFF_ACCOUNT",
            "No staff account found for this email. Contact your gym admin.",
        )

    # Link Google ID if not already linked
    if not staff.google_id:
        staff.google_id = google_id
        session.add(staff)
        session.commit()
        session.refresh(staff)

    staff_token = _build_staff_token(staff)

    # Include gym name for frontend
    gym_name = staff.gym.name if staff.gym else ""

    frontend_redirect = request.session.pop("oauth_redirect_uri", None)
    if frontend_redirect:
        return build_oauth_redirect_response(
            frontend_redirect,
            {
                "access_token": staff_token.access_token,
                "refresh_token": staff_token.refresh_token,
                "token_type": "bearer",
                "staff_id": staff_token.staff_id,
                "role": staff_token.role,
                "gym_id": staff_token.gym_id,
                "gym_name": gym_name,
            },
        )

    return staff_token


# =============================================================================
# Staff Apple OAuth Endpoints
# =============================================================================


@router.get("/apple")
async def staff_apple_login(
    request: Request,
    redirect_uri: str | None = None,
) -> Response:
    """Initiate Apple OAuth flow for staff."""
    if not settings.APPLE_CLIENT_ID or not settings.APPLE_PRIVATE_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "OAUTH_NOT_CONFIGURED",
                "message": "Apple Sign In is not configured",
                "details": {},
            },
        )

    from app.core.oauth import oauth

    if redirect_uri:
        from app.core.oauth_utils import validate_oauth_redirect_uri

        validate_oauth_redirect_uri(redirect_uri)
        request.session["oauth_redirect_uri"] = redirect_uri

    apple_redirect = settings.APPLE_STAFF_REDIRECT_URI
    return await oauth.apple.authorize_redirect(request, apple_redirect)  # type: ignore[no-any-return]


@router.post("/apple/callback", response_model=None)
async def staff_apple_callback(
    request: Request,
    session: SessionDep,
) -> StaffToken | Response:
    """Handle Apple OAuth callback for staff (link-only, no auto-creation).

    Apple uses response_mode=form_post, so this is a POST endpoint.
    Staff must already exist. Links apple_id if not already linked.
    """
    import jwt as pyjwt

    from app.core.oauth import generate_apple_client_secret, oauth
    from app.core.oauth_utils import build_oauth_redirect_response

    def _oauth_error(code: str, message: str, http_status: int = 400) -> Response:
        frontend_redirect = request.session.pop("oauth_redirect_uri", None)
        if frontend_redirect:
            return build_oauth_redirect_response(
                frontend_redirect, {"error": code, "error_message": message}
            )
        raise HTTPException(
            status_code=http_status,
            detail={"code": code, "message": message, "details": {}},
        )

    if not settings.APPLE_CLIENT_ID or not settings.APPLE_PRIVATE_KEY:
        return _oauth_error(
            "OAUTH_NOT_CONFIGURED", "Apple Sign In is not configured", 503
        )

    try:
        client_secret = generate_apple_client_secret()
        oauth.apple.client_secret = client_secret
        token = await oauth.apple.authorize_access_token(request)
    except Exception:
        return _oauth_error("INVALID_OAUTH_STATE", "Invalid or expired OAuth state")

    id_token = token.get("id_token")
    if not id_token:
        return _oauth_error(
            "OAUTH_USER_INFO_FAILED", "Failed to get ID token from Apple"
        )

    try:
        decoded = pyjwt.decode(id_token, options={"verify_signature": False})
    except Exception:
        return _oauth_error("OAUTH_USER_INFO_FAILED", "Failed to decode Apple ID token")

    apple_id = decoded.get("sub")
    email = decoded.get("email")

    if not apple_id:
        return _oauth_error(
            "OAUTH_USER_INFO_FAILED", "Apple ID token missing required 'sub' claim"
        )
    if not email:
        return _oauth_error(
            "OAUTH_NO_EMAIL", "Apple account does not have an email address"
        )

    # Find existing staff by apple_id or email (link-only, no creation)
    staff = session.exec(
        select(Staff).where(or_(Staff.apple_id == apple_id, Staff.email == email))
    ).first()

    if not staff or not staff.is_active:
        return _oauth_error(
            "NO_STAFF_ACCOUNT",
            "No staff account found for this email. Contact your gym admin.",
        )

    # Link Apple ID if not already linked
    if not staff.apple_id:
        staff.apple_id = apple_id
        session.add(staff)
        session.commit()
        session.refresh(staff)

    staff_token = _build_staff_token(staff)
    gym_name = staff.gym.name if staff.gym else ""

    frontend_redirect = request.session.pop("oauth_redirect_uri", None)
    if frontend_redirect:
        return build_oauth_redirect_response(
            frontend_redirect,
            {
                "access_token": staff_token.access_token,
                "refresh_token": staff_token.refresh_token,
                "token_type": "bearer",
                "staff_id": staff_token.staff_id,
                "role": staff_token.role,
                "gym_id": staff_token.gym_id,
                "gym_name": gym_name,
            },
        )

    return staff_token
