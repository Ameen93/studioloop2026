"""Gym onboarding endpoints (Epic 2).

Implements Story 2.1: Gym registration and owner account creation.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import EmailStr, HttpUrl, field_validator, model_validator
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, SQLModel, select

from app.api.deps import CurrentStaff, RequireOwnerOrManager, SessionDep
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


class GymProfileUpdateRequest(SQLModel):
    """Payload to configure gym public profile (Story 2.2)."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    tagline: str | None = Field(default=None, max_length=180)
    contact_email: EmailStr | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, min_length=8, max_length=50)
    logo_url: HttpUrl | None = None
    cover_photo_urls: list[HttpUrl] | None = None
    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    province: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    country: str | None = Field(default=None, min_length=2, max_length=2)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    @model_validator(mode="after")
    def validate_non_empty_update(self) -> "GymProfileUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()

    @field_validator("cover_photo_urls")
    @classmethod
    def validate_cover_photo_count(
        cls, value: list[HttpUrl] | None
    ) -> list[HttpUrl] | None:
        if value is not None and len(value) > 10:
            raise ValueError("A maximum of 10 cover photos is allowed")
        return value


class GymProfileResponse(SQLModel):
    """Gym profile response for owner dashboard + public view."""

    gym_id: UUID
    slug: str
    name: str
    description: str | None
    tagline: str | None
    contact_email: str | None
    contact_phone: str | None
    logo_url: str | None
    cover_photo_urls: list[str]
    address_line1: str | None
    address_line2: str | None
    city: str | None
    province: str | None
    postal_code: str | None
    country: str
    latitude: float | None
    longitude: float | None


def _serialize_gym_profile(gym: Gym) -> GymProfileResponse:
    return GymProfileResponse(
        gym_id=gym.id,
        slug=gym.slug,
        name=gym.name,
        description=gym.description,
        tagline=gym.tagline,
        contact_email=gym.email,
        contact_phone=gym.phone,
        logo_url=gym.logo_url,
        cover_photo_urls=gym.cover_photo_urls,
        address_line1=gym.address_line1,
        address_line2=gym.address_line2,
        city=gym.city,
        province=gym.province,
        postal_code=gym.postal_code,
        country=gym.country,
        latitude=gym.latitude,
        longitude=gym.longitude,
    )


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


@router.get(
    "/me/profile",
    response_model=GymProfileResponse,
    dependencies=[RequireOwnerOrManager],
)
def get_my_gym_profile(
    session: SessionDep,
    current_staff: CurrentStaff,
) -> GymProfileResponse:
    """Get current staff member's gym profile for management app."""
    gym = session.get(Gym, current_staff.gym_id)
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {},
            },
        )

    return _serialize_gym_profile(gym)


@router.patch(
    "/me/profile",
    response_model=GymProfileResponse,
    dependencies=[RequireOwnerOrManager],
)
def update_my_gym_profile(
    session: SessionDep,
    current_staff: CurrentStaff,
    payload: GymProfileUpdateRequest,
) -> GymProfileResponse:
    """Partially update current staff member's gym public profile (Story 2.2)."""
    gym = session.get(Gym, current_staff.gym_id)
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {},
            },
        )

    updates = payload.model_dump(exclude_unset=True)

    if "contact_phone" in updates:
        try:
            updates["contact_phone"] = validate_sa_phone(updates["contact_phone"])
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_PHONE_FORMAT",
                    "message": str(e),
                    "details": {"field": "contact_phone"},
                },
            )

    field_map = {
        "name": "name",
        "description": "description",
        "tagline": "tagline",
        "contact_email": "email",
        "contact_phone": "phone",
        "logo_url": "logo_url",
        "cover_photo_urls": "cover_photo_urls",
        "address_line1": "address_line1",
        "address_line2": "address_line2",
        "city": "city",
        "province": "province",
        "postal_code": "postal_code",
        "country": "country",
        "latitude": "latitude",
        "longitude": "longitude",
    }

    for request_field, model_field in field_map.items():
        if request_field not in updates:
            continue

        value = updates[request_field]
        if request_field == "logo_url" and value is not None:
            value = str(value)
        if request_field == "cover_photo_urls" and value is not None:
            value = [str(url) for url in value]

        setattr(gym, model_field, value)

    session.add(gym)
    session.commit()
    session.refresh(gym)

    return _serialize_gym_profile(gym)


@router.get("/{gym_slug}/profile", response_model=GymProfileResponse)
def get_public_gym_profile(
    session: SessionDep,
    gym_slug: str,
) -> GymProfileResponse:
    """Public profile endpoint consumed by marketplace/app clients."""
    gym = session.exec(select(Gym).where(Gym.slug == gym_slug.lower())).first()
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {},
            },
        )

    return _serialize_gym_profile(gym)
