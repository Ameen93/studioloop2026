"""Gym registration and management routes.

Story 2.1: Gym Registration and Owner Account
Implements gym owner registration which creates Consumer, Gym, and Staff records.
"""

import re

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import SessionDep
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import (
    Consumer,
    Gym,
    GymRegistrationCreate,
    GymRegistrationResponse,
    Staff,
    StaffRole,
    UserRole,
)
from app.utils import (
    generate_email_verification_email,
    generate_email_verification_token,
    send_email,
)

router = APIRouter(prefix="/auth/gym", tags=["gym-auth"])


def generate_unique_slug(name: str, session: SessionDep) -> str:
    """Generate unique URL-friendly slug from gym name.

    Converts name to lowercase, replaces non-alphanumeric with hyphens,
    and appends number suffix if slug already exists.

    Args:
        name: Gym display name
        session: Database session for uniqueness check

    Returns:
        Unique slug string (e.g., "my-awesome-gym" or "my-awesome-gym-1")
    """
    # Convert to lowercase and replace non-alphanumeric with hyphens
    base_slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    # Ensure slug is not empty
    if not base_slug:
        base_slug = "gym"

    # Check uniqueness and append suffix if needed
    slug = base_slug
    counter = 1
    while session.exec(select(Gym).where(Gym.slug == slug)).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


@router.post(
    "/register",
    response_model=GymRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_gym(
    session: SessionDep,
    registration_data: GymRegistrationCreate,
) -> GymRegistrationResponse:
    """Register a new gym with owner account (Story 2.1).

    Creates three linked records:
    1. Consumer with role=owner
    2. Gym with generated slug
    3. Staff linking owner to gym with role=owner

    Sends verification email to the owner's email address.

    Args:
        session: Database session
        registration_data: Owner and gym details

    Returns:
        GymRegistrationResponse with owner_id, gym_id, staff_id, and gym_slug

    Raises:
        HTTPException: 400 if email already exists (EMAIL_ALREADY_EXISTS)
    """
    # Check for duplicate email (AC #1: unique email for owner)
    existing_consumer = session.exec(
        select(Consumer).where(Consumer.email == registration_data.email)
    ).first()

    if existing_consumer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "EMAIL_ALREADY_EXISTS",
                "message": "An account with this email already exists",
                "details": {"field": "email"},
            },
        )

    # Also check Staff table to prevent duplicate staff emails
    existing_staff = session.exec(
        select(Staff).where(Staff.email == registration_data.email)
    ).first()

    if existing_staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "EMAIL_ALREADY_EXISTS",
                "message": "An account with this email already exists",
                "details": {"field": "email"},
            },
        )

    # Generate unique slug (AC #5: unique URL-friendly slug)
    slug = generate_unique_slug(registration_data.gym_name, session)

    # Hash password once for both Consumer and Staff (ARCH-11: Argon2)
    hashed_password = get_password_hash(registration_data.password)

    # Create Consumer with role=owner (AC #1)
    consumer = Consumer(
        email=registration_data.email,
        first_name=registration_data.first_name,
        last_name=registration_data.last_name,
        hashed_password=hashed_password,
        role=UserRole.OWNER,  # CRITICAL: Set role to owner
        is_email_verified=False,
    )
    session.add(consumer)
    session.flush()  # Get consumer.id before creating Gym

    # Create Gym record (AC #2, #5)
    gym = Gym(
        name=registration_data.gym_name,
        slug=slug,
        contact_email=registration_data.gym_contact_email or registration_data.email,
        contact_phone=registration_data.gym_contact_phone,
    )
    session.add(gym)
    session.flush()  # Get gym.id before creating Staff

    # Create Staff record linking owner to gym (AC #3)
    staff = Staff(
        email=registration_data.email,
        first_name=registration_data.first_name,
        last_name=registration_data.last_name,
        hashed_password=hashed_password,
        role=StaffRole.OWNER,  # CRITICAL: Staff role is owner
        gym_id=gym.id,
        is_email_verified=False,
    )
    session.add(staff)

    # Commit all records together
    session.commit()
    session.refresh(consumer)
    session.refresh(gym)
    session.refresh(staff)

    # Send verification email (AC #4)
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

    return GymRegistrationResponse(
        owner_id=consumer.id,
        gym_id=gym.id,
        staff_id=staff.id,
        email=consumer.email,
        gym_name=gym.name,
        gym_slug=gym.slug,
        message="Registration successful. Please verify your email.",
    )
