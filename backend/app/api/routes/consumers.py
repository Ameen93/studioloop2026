"""Consumer authentication routes.

Handles consumer registration and email verification.
Implements ARCH-11 (Argon2 password hashing) and ARCH-28 (error format).
"""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import SessionDep
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Message
from app.models.consumer import Consumer, ConsumerCreate, ConsumerPublic, UserRole
from app.utils import (
    generate_email_verification_email,
    generate_email_verification_token,
    send_email,
    verify_email_verification_token,
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
