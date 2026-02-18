"""Gym onboarding endpoints (Epic 2).

Implements Story 2.1: Gym registration and owner account creation.
"""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import EmailStr, HttpUrl, field_validator, model_validator
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, SQLModel, select

from app.api.deps import CurrentStaff, RequireOwnerOrManager, SessionDep
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Gym, GymClosure, Staff, StaffRole
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


class GymClosureItem(SQLModel):
    id: UUID
    closure_date: date
    reason: str | None = None


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
    business_hours: dict[str, dict[str, str | bool | None]]
    holiday_closures: list[GymClosureItem]
    address_line1: str | None
    address_line2: str | None
    city: str | None
    province: str | None
    postal_code: str | None
    country: str
    latitude: float | None
    longitude: float | None


class GymBusinessHoursUpdateRequest(SQLModel):
    """Weekly operating hours by weekday."""

    business_hours: dict[str, dict[str, str | bool | None]]

    @field_validator("business_hours")
    @classmethod
    def validate_business_hours(
        cls, value: dict[str, dict[str, str | bool | None]]
    ) -> dict[str, dict[str, str | bool | None]]:
        allowed_days = {
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        }
        for day, config in value.items():
            if day not in allowed_days:
                raise ValueError(f"Invalid day: {day}")
            if "is_closed" not in config:
                raise ValueError(f"Missing is_closed for {day}")
            if config.get("is_closed") is False:
                if not config.get("open_time") or not config.get("close_time"):
                    raise ValueError(
                        f"open_time and close_time are required when {day} is open"
                    )
        return value


class GymBusinessHoursResponse(SQLModel):
    gym_id: UUID
    business_hours: dict[str, dict[str, str | bool | None]]


class GymCancellationPolicyUpdateRequest(SQLModel):
    cancellation_window_hours: int = Field(ge=0, le=168)
    no_show_penalty: str

    @field_validator("no_show_penalty")
    @classmethod
    def validate_no_show_penalty(cls, value: str) -> str:
        allowed = {"none", "credit_lost", "fee"}
        if value not in allowed:
            raise ValueError("no_show_penalty must be one of: none, credit_lost, fee")
        return value


class GymCancellationPolicyResponse(SQLModel):
    gym_id: UUID
    cancellation_window_hours: int
    no_show_penalty: str


class GymClosureCreateRequest(SQLModel):
    closure_date: date
    reason: str | None = Field(default=None, max_length=255)


class GymClosureResponse(SQLModel):
    id: UUID
    gym_id: UUID
    closure_date: date
    reason: str | None = None


def _get_gym_closures(
    session: SessionDep,
    gym_id: UUID,
    include_past: bool = True,
) -> list[GymClosure]:
    stmt = select(GymClosure).where(GymClosure.gym_id == gym_id)
    if not include_past:
        stmt = stmt.where(GymClosure.closure_date >= date.today())
    return session.exec(stmt.order_by(GymClosure.closure_date.asc())).all()


def _get_cancellation_policy(gym: Gym) -> GymCancellationPolicyResponse:
    settings_data = gym.settings or {}

    raw_window = settings_data.get("cancellation_window_hours", 24)
    try:
        cancellation_window_hours = int(raw_window)
    except (TypeError, ValueError):
        cancellation_window_hours = 24
    cancellation_window_hours = max(0, min(168, cancellation_window_hours))

    no_show_penalty = str(settings_data.get("no_show_penalty", "none"))
    if no_show_penalty not in {"none", "credit_lost", "fee"}:
        no_show_penalty = "none"

    return GymCancellationPolicyResponse(
        gym_id=gym.id,
        cancellation_window_hours=cancellation_window_hours,
        no_show_penalty=no_show_penalty,
    )


def _serialize_gym_profile(
    gym: Gym, holiday_closures: list[GymClosure]
) -> GymProfileResponse:
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
        business_hours=gym.business_hours,
        holiday_closures=[
            GymClosureItem(id=closure.id, closure_date=closure.closure_date, reason=closure.reason)
            for closure in holiday_closures
        ],
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

    closures = _get_gym_closures(session, gym.id)
    return _serialize_gym_profile(gym, closures)


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
        "business_hours": "business_hours",
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

    closures = _get_gym_closures(session, gym.id)
    return _serialize_gym_profile(gym, closures)


@router.get(
    "/me/operating_hours",
    response_model=GymBusinessHoursResponse,
    dependencies=[RequireOwnerOrManager],
)
def get_my_gym_operating_hours(
    session: SessionDep,
    current_staff: CurrentStaff,
) -> GymBusinessHoursResponse:
    gym = session.get(Gym, current_staff.gym_id)
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "GYM_NOT_FOUND", "message": "Gym not found", "details": {}},
        )

    return GymBusinessHoursResponse(gym_id=gym.id, business_hours=gym.business_hours)


@router.patch(
    "/me/operating_hours",
    response_model=GymBusinessHoursResponse,
    dependencies=[RequireOwnerOrManager],
)
def update_my_gym_operating_hours(
    session: SessionDep,
    current_staff: CurrentStaff,
    payload: GymBusinessHoursUpdateRequest,
) -> GymBusinessHoursResponse:
    gym = session.get(Gym, current_staff.gym_id)
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "GYM_NOT_FOUND", "message": "Gym not found", "details": {}},
        )

    gym.business_hours = payload.business_hours
    session.add(gym)
    session.commit()
    session.refresh(gym)

    return GymBusinessHoursResponse(gym_id=gym.id, business_hours=gym.business_hours)


@router.get(
    "/me/cancellation_policy",
    response_model=GymCancellationPolicyResponse,
    dependencies=[RequireOwnerOrManager],
)
def get_my_gym_cancellation_policy(
    session: SessionDep,
    current_staff: CurrentStaff,
) -> GymCancellationPolicyResponse:
    gym = session.get(Gym, current_staff.gym_id)
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "GYM_NOT_FOUND", "message": "Gym not found", "details": {}},
        )

    return _get_cancellation_policy(gym)


@router.patch(
    "/me/cancellation_policy",
    response_model=GymCancellationPolicyResponse,
    dependencies=[RequireOwnerOrManager],
)
def update_my_gym_cancellation_policy(
    session: SessionDep,
    current_staff: CurrentStaff,
    payload: GymCancellationPolicyUpdateRequest,
) -> GymCancellationPolicyResponse:
    gym = session.get(Gym, current_staff.gym_id)
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "GYM_NOT_FOUND", "message": "Gym not found", "details": {}},
        )

    settings_data = dict(gym.settings or {})
    settings_data["cancellation_window_hours"] = payload.cancellation_window_hours
    settings_data["no_show_penalty"] = payload.no_show_penalty
    gym.settings = settings_data

    session.add(gym)
    session.commit()
    session.refresh(gym)

    return _get_cancellation_policy(gym)


@router.get(
    "/me/closures",
    response_model=list[GymClosureResponse],
    dependencies=[RequireOwnerOrManager],
)
def list_my_gym_closures(
    session: SessionDep,
    current_staff: CurrentStaff,
) -> list[GymClosureResponse]:
    gym = session.get(Gym, current_staff.gym_id)
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "GYM_NOT_FOUND", "message": "Gym not found", "details": {}},
        )

    closures = _get_gym_closures(session, gym.id)
    return [
        GymClosureResponse(
            id=closure.id,
            gym_id=closure.gym_id,
            closure_date=closure.closure_date,
            reason=closure.reason,
        )
        for closure in closures
    ]


@router.post(
    "/me/closures",
    response_model=GymClosureResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireOwnerOrManager],
)
def add_my_gym_closure(
    session: SessionDep,
    current_staff: CurrentStaff,
    payload: GymClosureCreateRequest,
) -> GymClosureResponse:
    gym = session.get(Gym, current_staff.gym_id)
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "GYM_NOT_FOUND", "message": "Gym not found", "details": {}},
        )

    existing = session.exec(
        select(GymClosure).where(
            GymClosure.gym_id == gym.id,
            GymClosure.closure_date == payload.closure_date,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CLOSURE_ALREADY_EXISTS",
                "message": "A closure already exists for this date",
                "details": {"closure_date": str(payload.closure_date)},
            },
        )

    closure = GymClosure(
        gym_id=gym.id,
        closure_date=payload.closure_date,
        reason=payload.reason,
    )
    session.add(closure)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CLOSURE_ALREADY_EXISTS",
                "message": "A closure already exists for this date",
                "details": {"closure_date": str(payload.closure_date)},
            },
        )
    session.refresh(closure)

    return GymClosureResponse(
        id=closure.id,
        gym_id=closure.gym_id,
        closure_date=closure.closure_date,
        reason=closure.reason,
    )


@router.delete(
    "/me/closures/{closure_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[RequireOwnerOrManager],
)
def delete_my_gym_closure(
    session: SessionDep,
    current_staff: CurrentStaff,
    closure_id: UUID,
) -> None:
    closure = session.exec(
        select(GymClosure).where(
            GymClosure.id == closure_id,
            GymClosure.gym_id == current_staff.gym_id,
        )
    ).first()
    if not closure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CLOSURE_NOT_FOUND",
                "message": "Closure not found",
                "details": {},
            },
        )

    session.delete(closure)
    session.commit()


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

    closures = _get_gym_closures(session, gym.id, include_past=False)
    return _serialize_gym_profile(gym, closures)
