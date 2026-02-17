"""Gym onboarding endpoints (Epic 2).

Implements Story 2.1: Gym registration and owner account creation.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import EmailStr, field_validator
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, SQLModel, select

from app.api.deps import SessionDep
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Gym, Staff, StaffRole
from app.utils import (
    generate_email_verification_email,
    generate_email_verification_token,
    send_email,
    validate_sa_phone,
)

router = APIRouter(prefix="/gyms", tags=["gyms"])


class GymRegistrationRequest(SQLModel):
    """Payload to register a gym and owner account."""

    owner_email: EmailStr = Field(max_length=255)
    owner_password: str = Field(min_length=8, max_length=128)
    owner_first_name: str = Field(min_length=1, max_length=100)
    owner_last_name: str = Field(min_length=1, max_length=100)
    gym_name: str = Field(min_length=1, max_length=255)
    gym_slug: str = Field(min_length=1, max_length=100)
    contact_email: EmailStr = Field(max_length=255)
    contact_phone: str = Field(min_length=8, max_length=50)

    @field_validator("gym_slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        """Enforce URL-safe lowercase slug format."""
        slug = value.strip().lower()
        if not slug:
            raise ValueError("Gym slug cannot be empty")

        allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-")
        if any(char not in allowed for char in slug):
            raise ValueError(
                "Gym slug must contain only lowercase letters, numbers, and hyphens"
            )

        if slug.startswith("-") or slug.endswith("-") or "--" in slug:
            raise ValueError("Gym slug format is invalid")

        return slug


class GymRegistrationResponse(SQLModel):
    """Response returned after successful gym registration."""

    gym_id: UUID
    owner_staff_id: UUID
    message: str


@router.post(
    "/register",
    response_model=GymRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_gym(
    session: SessionDep,
    payload: GymRegistrationRequest,
) -> GymRegistrationResponse:
    """Register a gym and create the owner as a staff account.

    AC mapping (Story 2.1):
    - Create gym record (UUID PK)
    - Create owner staff record linked via gym_id with role=owner
    - Send verification email to owner when email is enabled
    """
    # Ensure slug uniqueness
    existing_gym = session.exec(select(Gym).where(Gym.slug == payload.gym_slug)).first()
    if existing_gym:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GYM_SLUG_ALREADY_EXISTS",
                "message": "A gym with this slug already exists",
                "details": {"field": "gym_slug"},
            },
        )

    # Ensure owner email is unique in staff namespace
    existing_staff = session.exec(
        select(Staff).where(Staff.email == payload.owner_email)
    ).first()
    if existing_staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "OWNER_EMAIL_ALREADY_EXISTS",
                "message": "An owner/staff account with this email already exists",
                "details": {"field": "owner_email"},
            },
        )

    try:
        normalized_phone = validate_sa_phone(payload.contact_phone)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PHONE_FORMAT",
                "message": str(e),
                "details": {"field": "contact_phone"},
            },
        )

    gym = Gym(
        name=payload.gym_name,
        slug=payload.gym_slug,
        email=payload.contact_email,
        phone=normalized_phone,
        is_active=True,
    )
    session.add(gym)
    session.flush()

    owner_staff = Staff(
        gym_id=gym.id,
        email=payload.owner_email,
        hashed_password=get_password_hash(payload.owner_password),
        first_name=payload.owner_first_name,
        last_name=payload.owner_last_name,
        role=StaffRole.OWNER,
        phone=normalized_phone,
        is_email_verified=False,
        is_active=True,
    )
    session.add(owner_staff)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "REGISTRATION_CONFLICT",
                "message": "Gym registration conflicts with existing records",
                "details": {},
            },
        )

    session.refresh(gym)
    session.refresh(owner_staff)

    if settings.emails_enabled:
        token = generate_email_verification_token(owner_staff.email)
        email_data = generate_email_verification_email(
            email_to=owner_staff.email,
            token=token,
        )
        send_email(
            email_to=owner_staff.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    return GymRegistrationResponse(
        gym_id=gym.id,
        owner_staff_id=owner_staff.id,
        message="Gym and owner account created. Verification email sent if enabled.",
    )
