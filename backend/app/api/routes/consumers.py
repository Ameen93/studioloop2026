"""Consumer authentication routes.

Handles consumer registration, login, email verification, and token refresh.
Implements ARCH-11 (Argon2 password hashing), ARCH-12 (JWT tokens), and ARCH-28 (error format).
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
from app.models.consumer import (
    Consumer,
    ConsumerCreate,
    ConsumerLoginRequest,
    ConsumerPublic,
    ConsumerToken,
    UserRole,
)
from app.utils import (
    generate_email_verification_email,
    generate_email_verification_token,
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
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
def login_consumer(
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
def forgot_password(
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
