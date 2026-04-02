"""Consumer authentication routes.

Handles consumer registration, login, email verification, and token refresh.
Implements ARCH-11 (Argon2 password hashing), ARCH-12 (JWT tokens), and ARCH-28 (error format).
"""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import ValidationError, field_validator
from sqlmodel import Field, SQLModel, or_, select
from starlette.responses import Response

from app.api.deps import CurrentConsumer, SessionDep
from app.core import security
from app.core.config import settings
from app.core.rate_limit import RATE_AUTH, RATE_PASSWORD_RESET, limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    needs_rehash,
    validate_password_strength,
    verify_password,
)
from app.models import (
    ForgotPasswordRequest,
    Message,
    NewPassword,
    RefreshTokenRequest,
    TokenPayload,
)
from app.models.consumer import (
    AccountDeletionRequest,
    AuthProvider,
    Consumer,
    ConsumerCreate,
    ConsumerLoginRequest,
    ConsumerPublic,
    ConsumerToken,
    ConsumerUpdate,
    UserRole,
)
from app.utils import (
    generate_account_deletion_email,
    generate_email_verification_email,
    generate_email_verification_token,
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    validate_sa_phone,
    verify_email_verification_token,
    verify_password_reset_token,
)

router = APIRouter(prefix="/auth/consumer", tags=["consumer-auth"])


@router.post(
    "/register",
    response_model=ConsumerPublic,
    status_code=status.HTTP_201_CREATED,
)
def register_consumer(
    session: SessionDep,
    consumer_in: ConsumerCreate,
) -> Consumer:
    """Register a new consumer account.

    Creates a consumer with the CONSUMER role. Sends a verification
    email that must be confirmed before the user can log in.

    Args:
        session: Database session
        consumer_in: Registration data (email, password, first_name, last_name)

    Returns:
        ConsumerPublic: The created consumer (password excluded)

    Raises:
        HTTPException: 400 if email already exists
    """
    # Check for duplicate email
    existing = session.exec(
        select(Consumer).where(Consumer.email == consumer_in.email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "EMAIL_ALREADY_EXISTS",
                "message": "An account with this email already exists",
                "details": {"field": "email"},
            },
        )

    # Create consumer with Argon2-hashed password
    consumer = Consumer(
        email=consumer_in.email,
        first_name=consumer_in.first_name,
        last_name=consumer_in.last_name,
        phone=consumer_in.phone,
        hashed_password=get_password_hash(consumer_in.password),
        role=UserRole.CONSUMER,
        is_email_verified=False,
    )

    session.add(consumer)
    session.commit()
    session.refresh(consumer)

    # Send verification email (only if email is enabled)
    if settings.emails_enabled:
        token = generate_email_verification_token(consumer.email)
        email_data = generate_email_verification_email(
            email_to=consumer.email,
            token=token,
        )
        send_email(
            email_to=consumer.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    return consumer


@router.get("/verify-email")
def verify_email(
    session: SessionDep,
    token: str,
) -> Message:
    """Verify a consumer's email address.

    Validates the verification token and marks the consumer's
    email as verified.

    Args:
        session: Database session
        token: JWT verification token from email link

    Returns:
        Message confirming verification success

    Raises:
        HTTPException: 400 if token is invalid or expired
        HTTPException: 404 if consumer not found
    """
    email = verify_email_verification_token(token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired verification token",
                "details": {},
            },
        )

    consumer = session.exec(select(Consumer).where(Consumer.email == email)).first()

    if not consumer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CONSUMER_NOT_FOUND",
                "message": "Consumer not found",
                "details": {"email": email},
            },
        )

    if consumer.is_email_verified:
        return Message(message="Email already verified")

    consumer.is_email_verified = True
    session.add(consumer)
    session.commit()

    return Message(message="Email verified successfully")


@router.post("/resend-verification")
def resend_verification_email(
    session: SessionDep,
    email: str,
) -> Message:
    """Resend the verification email.

    Generates a new verification token and sends it to the
    consumer's email address.

    Args:
        session: Database session
        email: Consumer's email address

    Returns:
        Message confirming email was sent (always returns success
        to prevent email enumeration)
    """
    consumer = session.exec(select(Consumer).where(Consumer.email == email)).first()

    # Always return success to prevent email enumeration
    if not consumer:
        return Message(message="If the email exists, a verification link has been sent")

    if consumer.is_email_verified:
        return Message(message="If the email exists, a verification link has been sent")

    if settings.emails_enabled:
        token = generate_email_verification_token(consumer.email)
        email_data = generate_email_verification_email(
            email_to=consumer.email,
            token=token,
        )
        send_email(
            email_to=consumer.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    return Message(message="If the email exists, a verification link has been sent")


@router.post("/login", response_model=ConsumerToken)
@limiter.limit(RATE_AUTH)
def login_consumer(
    request: Request,  # noqa: ARG001 — required by slowapi limiter
    session: SessionDep,
    login_data: ConsumerLoginRequest,
) -> ConsumerToken:
    """Authenticate consumer and return JWT tokens (ARCH-10, ARCH-12).

    Validates credentials and returns access + refresh tokens.
    Upgrades legacy bcrypt hashes to Argon2 on successful login.

    Args:
        session: Database session
        login_data: Email and password

    Returns:
        ConsumerToken with access_token, refresh_token, token_type

    Raises:
        HTTPException: 401 if credentials invalid (INVALID_CREDENTIALS)
        HTTPException: 403 if email not verified (EMAIL_NOT_VERIFIED)
    """
    # Find consumer by email
    consumer = session.exec(
        select(Consumer).where(Consumer.email == login_data.email)
    ).first()

    # Use same error for invalid email or password (prevent enumeration)
    if not consumer or not consumer.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
                "details": {},
            },
        )

    if not verify_password(login_data.password, consumer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
                "details": {},
            },
        )

    # Check email verification (AC #5)
    if not consumer.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "EMAIL_NOT_VERIFIED",
                "message": "Please verify your email before logging in",
                "details": {"email": consumer.email},
            },
        )

    # Check if account is active (reject soft-deleted/deactivated accounts)
    if not consumer.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
                "details": {},
            },
        )

    # Upgrade legacy bcrypt hash to Argon2 (ARCH-11)
    if needs_rehash(consumer.hashed_password):
        consumer.hashed_password = get_password_hash(login_data.password)
        session.add(consumer)
        session.commit()

    # Generate tokens (ARCH-12) with token_version for rotation
    access_token = create_access_token(
        subject=str(consumer.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        subject=str(consumer.id),
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_version=consumer.token_version,
    )

    return ConsumerToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=ConsumerToken)
def refresh_consumer_token(
    session: SessionDep,
    refresh_data: RefreshTokenRequest,
) -> ConsumerToken:
    """Refresh consumer access token using refresh token (ARCH-12).

    Validates the refresh token and issues a new access + refresh token pair.
    Token version is validated and incremented to invalidate old refresh tokens.

    Args:
        session: Database session
        refresh_data: Contains the refresh token

    Returns:
        ConsumerToken with new access_token and refresh_token

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

    # Get consumer from token subject
    consumer = session.get(Consumer, token_data.sub)

    # Return same error for missing/inactive consumer (no enumeration)
    if not consumer or not consumer.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired refresh token",
                "details": {},
            },
        )

    # Validate token version for rotation (reject replayed tokens)
    if token_data.token_version != consumer.token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired refresh token",
                "details": {},
            },
        )

    # Increment token version to invalidate old refresh tokens
    consumer.token_version += 1
    session.add(consumer)
    session.commit()
    session.refresh(consumer)

    # Generate new token pair with new version
    access_token = create_access_token(
        subject=str(consumer.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        subject=str(consumer.id),
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_version=consumer.token_version,
    )

    return ConsumerToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/forgot-password")
@limiter.limit(RATE_PASSWORD_RESET)
def forgot_password(
    request: Request,  # noqa: ARG001 — required by slowapi limiter
    session: SessionDep,
    request_data: ForgotPasswordRequest,
) -> Message:
    """Request password reset email (Story 1.5, AC #1, #5).

    Always returns success, regardless of whether email exists.
    Only sends email if consumer exists, is active, AND email is verified.
    This prevents email enumeration attacks.

    Args:
        session: Database session
        request_data: Contains the email address

    Returns:
        Message confirming request received (always success)
    """
    consumer = session.exec(
        select(Consumer).where(Consumer.email == request_data.email)
    ).first()

    # Only send email if consumer exists, is active, and email verified
    # But ALWAYS return success to prevent enumeration
    if consumer and consumer.is_active and consumer.is_email_verified:
        if settings.emails_enabled:
            token = generate_password_reset_token(
                request_data.email, account_type="consumer"
            )
            email_data = generate_reset_password_email(
                email_to=consumer.email,
                email=request_data.email,
                token=token,
            )
            send_email(
                email_to=consumer.email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )

    return Message(message="If the email exists, a password reset link has been sent")


@router.post("/reset-password")
def reset_password(
    session: SessionDep,
    request_data: NewPassword,
) -> Message:
    """Reset password using token from email (Story 1.5, AC #2, #3, #4).

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
        request_data.token, expected_account_type="consumer"
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

    consumer = session.exec(select(Consumer).where(Consumer.email == email)).first()

    # Use same error for not found/inactive to prevent enumeration
    if not consumer or not consumer.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired reset token",
                "details": {},
            },
        )

    # Update password with Argon2 hash (ARCH-11)
    consumer.hashed_password = get_password_hash(request_data.new_password)

    # CRITICAL: Invalidate all existing sessions (ARCH-12)
    consumer.token_version += 1

    session.add(consumer)
    session.commit()

    return Message(message="Password has been reset successfully")


@router.get("/me", response_model=ConsumerPublic)
def get_current_consumer_profile(
    current_consumer: CurrentConsumer,
) -> Consumer:
    """Get current consumer's profile (Story 1.6, AC #1).

    Returns the authenticated consumer's profile information.
    Requires a valid access token.

    Args:
        current_consumer: Authenticated consumer from JWT token

    Returns:
        ConsumerPublic with profile data (excludes sensitive fields)
    """
    return current_consumer


@router.patch("/me", response_model=ConsumerPublic)
def update_consumer_profile(
    session: SessionDep,
    current_consumer: CurrentConsumer,
    update_data: ConsumerUpdate,
) -> Consumer:
    """Update current consumer's profile (Story 1.6, AC #2, #3, #4).

    Allows partial updates - only provided fields are updated.
    Phone number must be in SA format (+27...) if provided.

    Args:
        session: Database session
        current_consumer: Authenticated consumer from JWT token
        update_data: Fields to update (first_name, last_name, phone)

    Returns:
        ConsumerPublic with updated profile data

    Raises:
        HTTPException: 400 INVALID_PHONE_FORMAT if phone format is invalid
    """
    # Validate phone if provided (not None and not empty string in update)
    update_dict = update_data.model_dump(exclude_unset=True)

    # Reject null for non-nullable fields
    non_nullable_fields = ["first_name", "last_name", "accepts_marketing"]
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
        setattr(current_consumer, field, value)

    session.add(current_consumer)
    session.commit()
    session.refresh(current_consumer)

    return current_consumer


@router.delete("/me", response_model=Message)
def delete_consumer_account(
    session: SessionDep,
    current_consumer: CurrentConsumer,
    deletion_request: AccountDeletionRequest,
) -> Message:
    """Delete consumer account (POPIA right to erasure - Story 1.7).

    Requires password confirmation for security. Marks account for
    deletion, invalidates all sessions, and schedules data cleanup
    within 30 days per POPIA requirements.

    Args:
        session: Database session
        current_consumer: Authenticated consumer from JWT token
        deletion_request: Password confirmation

    Returns:
        Message confirming deletion scheduled

    Raises:
        HTTPException: 401 INVALID_CREDENTIALS if password is wrong
    """
    # Verify password for security (prevent unauthorized deletion)
    # NOTE: Revisit for social login users (Stories 1.9/1.10) who may not have passwords
    assert current_consumer.hashed_password, "Consumer must have password set"
    if not verify_password(deletion_request.password, current_consumer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid password",
                "details": {},
            },
        )

    # Mark account for deletion using SoftDeleteMixin
    current_consumer.soft_delete()

    # Set deletion requested timestamp for 30-day countdown (NFR13)
    current_consumer.deletion_requested_at = datetime.now(timezone.utc)

    # CRITICAL: Invalidate ALL tokens by incrementing version (ARCH-12)
    current_consumer.token_version += 1

    session.add(current_consumer)
    session.commit()

    # Send confirmation email
    if settings.emails_enabled:
        email_data = generate_account_deletion_email(
            email_to=current_consumer.email,
            first_name=current_consumer.first_name,
        )
        send_email(
            email_to=current_consumer.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    return Message(
        message="Account deletion scheduled. Your data will be removed within 30 days."
    )


# =============================================================================
# Google OAuth Endpoints (Story 1.9, ARCH-14)
# =============================================================================


class SetPasswordRequest(SQLModel):
    """Request to set password for social-login-only user."""

    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def check_password_strength(cls, v: str) -> str:
        return validate_password_strength(v)


@router.get("/google")
async def google_login(
    request: Request,
    redirect_uri: str | None = None,
) -> Response:
    """Initiate Google OAuth flow (Story 1.9, AC #1).

    Redirects to Google's authorization endpoint with proper scopes.
    Uses session middleware for OAuth state management.

    Args:
        request: FastAPI request object (needed for Authlib)
        redirect_uri: Optional frontend URL to redirect to after OAuth completes

    Returns:
        RedirectResponse to Google's authorization endpoint

    Raises:
        HTTPException: 503 if Google OAuth is not configured
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

    google_redirect = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, google_redirect)  # type: ignore[no-any-return]


@router.get("/google/callback", response_model=None)
async def google_callback(
    request: Request,
    session: SessionDep,
) -> ConsumerToken | Response:
    """Handle Google OAuth callback (Story 1.9, AC #1, #2, #3, #5).

    Validates OAuth response, creates/links user account, and returns JWT tokens.
    If a redirect_uri was stored in session, redirects with tokens in URL fragment.
    Otherwise returns JSON (backward compatibility).

    Args:
        request: FastAPI request object (contains OAuth callback params)
        session: Database session

    Returns:
        ConsumerToken or RedirectResponse with tokens in fragment

    Raises:
        HTTPException: 400 if OAuth validation fails
        HTTPException: 503 if Google OAuth is not configured
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
    from app.core.oauth_utils import build_oauth_redirect_response

    # Helper: redirect errors to frontend if redirect_uri was set, else raise HTTP
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
    name = user_info.get("name", "")
    picture = user_info.get("picture")

    if not email:
        return _oauth_error(
            "OAUTH_NO_EMAIL", "Google account does not have an email address"
        )

    # Parse name into first/last
    name_parts = name.split(" ", 1)
    first_name = name_parts[0] if name_parts else "User"
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    # Find existing consumer by google_id OR email (AC #5: link existing accounts)
    consumer = session.exec(
        select(Consumer).where(
            or_(Consumer.google_id == google_id, Consumer.email == email)
        )
    ).first()

    if consumer:
        if not consumer.is_active:
            return _oauth_error(
                "ACCOUNT_DEACTIVATED", "This account has been deactivated", 403
            )

        # Existing user - link Google if not already linked
        if not consumer.google_id:
            consumer.google_id = google_id

        # Update avatar if user doesn't have one and Google provides picture (AC #2)
        if not consumer.avatar_url and picture:
            consumer.avatar_url = picture

        # Mark as email verified if not already (Google verified it)
        if not consumer.is_email_verified:
            consumer.is_email_verified = True

        session.add(consumer)
        session.commit()
        session.refresh(consumer)
    else:
        # New user - create account (AC #1)
        consumer = Consumer(
            email=email,
            first_name=first_name,
            last_name=last_name,
            google_id=google_id,
            avatar_url=picture,
            auth_provider=AuthProvider.GOOGLE,
            is_email_verified=True,  # Google verified it
            is_active=True,
            hashed_password=None,  # No password for social login
            role=UserRole.CONSUMER,
        )
        session.add(consumer)
        session.commit()
        session.refresh(consumer)

    # Generate JWT tokens (AC #3)
    access_token = create_access_token(
        subject=str(consumer.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        subject=str(consumer.id),
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_version=consumer.token_version,
    )

    # Redirect to frontend if redirect_uri was stored in session
    frontend_redirect = request.session.pop("oauth_redirect_uri", None)
    if frontend_redirect:
        from app.core.oauth_utils import build_oauth_redirect_response

        return build_oauth_redirect_response(
            frontend_redirect,
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            },
        )

    return ConsumerToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/set-password", response_model=Message)
def set_password(
    session: SessionDep,
    current_consumer: CurrentConsumer,
    request_data: SetPasswordRequest,
) -> Message:
    """Set password for a social-login-only user (Story 1.9, AC #4).

    Allows users who signed up via Google/Apple to add a password
    so they can also login via email.

    Args:
        session: Database session
        current_consumer: Authenticated consumer from JWT token
        request_data: Contains new_password

    Returns:
        Message confirming password was set

    Raises:
        HTTPException: 400 PASSWORD_ALREADY_SET if user already has a password
    """
    if current_consumer.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "PASSWORD_ALREADY_SET",
                "message": "Password is already set. Use change password instead.",
                "details": {},
            },
        )

    current_consumer.hashed_password = get_password_hash(request_data.new_password)
    session.add(current_consumer)
    session.commit()

    return Message(message="Password has been set successfully")


# =============================================================================
# Apple Sign In Endpoints (Story 1.10)
# =============================================================================


@router.get("/apple")
async def apple_login(
    request: Request,
    redirect_uri: str | None = None,
) -> Response:
    """Initiate Apple OAuth flow (Story 1.10, AC #1, #4).

    Redirects user to Apple's authorization endpoint for Sign in with Apple.
    Uses SessionMiddleware for CSRF protection via state parameter.

    Args:
        request: FastAPI request object (needed for Authlib)
        redirect_uri: Optional frontend URL to redirect to after OAuth completes

    Returns:
        RedirectResponse to Apple's authorization endpoint

    Raises:
        HTTPException: 503 if Apple Sign In is not configured
    """
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

    apple_redirect = settings.APPLE_REDIRECT_URI
    return await oauth.apple.authorize_redirect(request, apple_redirect)  # type: ignore[no-any-return]


@router.post("/apple/callback", response_model=None)
async def apple_callback(
    request: Request,
    session: SessionDep,
) -> ConsumerToken | Response:
    """Handle Apple OAuth callback (Story 1.10, AC #1, #2, #3, #5).

    Apple uses response_mode=form_post, so this is a POST endpoint.
    Validates OAuth response, creates/links user account, and returns JWT tokens.
    If a redirect_uri was stored in session, redirects with tokens in URL fragment.

    Args:
        request: FastAPI request object (contains OAuth callback form data)
        session: Database session

    Returns:
        ConsumerToken or RedirectResponse with tokens in fragment

    Raises:
        HTTPException: 400 if OAuth validation fails
        HTTPException: 403 if account is deactivated
        HTTPException: 503 if Apple Sign In is not configured
    """
    import json

    from app.core.oauth import generate_apple_client_secret, oauth
    from app.core.oauth_utils import build_oauth_redirect_response

    # Helper: redirect errors to frontend if redirect_uri was set, else raise HTTP
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

    # Get form data (Apple uses form_post response mode)
    form_data = await request.form()
    user_data_str = form_data.get("user")  # JSON string, only on first auth

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
        from app.core.apple_token import verify_apple_id_token

        decoded = verify_apple_id_token(id_token)
    except Exception:
        return _oauth_error("OAUTH_USER_INFO_FAILED", "Failed to verify Apple ID token")

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

    # Handle first-login name extraction (Apple only sends name on first auth)
    first_name = "Apple"
    last_name = "User"

    if user_data_str:
        try:
            user_data = json.loads(str(user_data_str))
            name_data = user_data.get("name", {})
            first_name = name_data.get("firstName", "Apple") or "Apple"
            last_name = name_data.get("lastName", "User") or "User"
        except (json.JSONDecodeError, TypeError):
            pass  # Use default names

    # Find existing consumer by apple_id OR email (AC #5: link existing accounts)
    consumer = session.exec(
        select(Consumer).where(
            or_(Consumer.apple_id == apple_id, Consumer.email == email)
        )
    ).first()

    if consumer:
        if not consumer.is_active:
            return _oauth_error(
                "ACCOUNT_DEACTIVATED", "This account has been deactivated", 403
            )

        # Existing user - link Apple if not already linked
        if not consumer.apple_id:
            consumer.apple_id = apple_id

        # Mark as email verified if not already (Apple verified it)
        if not consumer.is_email_verified:
            consumer.is_email_verified = True

        session.add(consumer)
        session.commit()
        session.refresh(consumer)
    else:
        # New user - create account (AC #1)
        # Note: Apple's Hide My Email relay addresses are supported (AC #3)
        consumer = Consumer(
            email=email,
            first_name=first_name,
            last_name=last_name,
            apple_id=apple_id,
            auth_provider=AuthProvider.APPLE,
            is_email_verified=True,  # Apple verified it
            is_active=True,
            hashed_password=None,  # No password for social login
            role=UserRole.CONSUMER,
        )
        session.add(consumer)
        session.commit()
        session.refresh(consumer)

    # Generate JWT tokens (AC #2)
    access_token = create_access_token(
        subject=str(consumer.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        subject=str(consumer.id),
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_version=consumer.token_version,
    )

    # Redirect to frontend if redirect_uri was stored in session
    frontend_redirect = request.session.pop("oauth_redirect_uri", None)
    if frontend_redirect:
        from app.core.oauth_utils import build_oauth_redirect_response

        return build_oauth_redirect_response(
            frontend_redirect,
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            },
        )

    return ConsumerToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )
