"""Gym registration and management routes.

Story 2.1: Gym Registration and Owner Account
Implements gym owner registration which creates Consumer, Gym, and Staff records.

Story 2.2: Gym Profile Configuration
Implements gym profile update, address update, and photo upload endpoints.
"""

import re
import uuid as uuid_module
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlmodel import select

from app.api.deps import (
    RequireOwnerOrManager,
    SessionDep,
    StaffGymDep,
)
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import (
    Consumer,
    Gym,
    GymAddressUpdate,
    GymPhotoDeleteRequest,
    GymProfileUpdate,
    GymPublic,
    GymRegistrationCreate,
    GymRegistrationResponse,
    PhotoUploadResponse,
    Staff,
    StaffRole,
    UserRole,
)
from app.utils import (
    generate_email_verification_email,
    generate_email_verification_token,
    send_email,
)


def validate_uuid(value: str, field_name: str = "id") -> UUID:
    """Validate and parse a UUID string.

    Args:
        value: String value to validate as UUID
        field_name: Name of field for error message

    Returns:
        Parsed UUID object

    Raises:
        HTTPException: 422 if value is not a valid UUID
    """
    try:
        return UUID(value)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "INVALID_UUID",
                "message": f"Invalid UUID format for {field_name}",
                "details": {"field": field_name, "value": value},
            },
        )


# File upload configuration
UPLOAD_DIR = Path(settings.UPLOAD_DIR if hasattr(settings, "UPLOAD_DIR") else "uploads")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

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


# =============================================================================
# Gym Management Router (Story 2.2)
# =============================================================================

gym_router = APIRouter(prefix="/gyms", tags=["gyms"])


@gym_router.get("/by-slug/{slug}", response_model=GymPublic)
def get_gym_by_slug(
    slug: str,
    session: SessionDep,
) -> Gym:
    """Get gym public profile by slug (no auth required).

    Args:
        slug: URL-friendly gym identifier
        session: Database session

    Returns:
        GymPublic with all profile fields

    Raises:
        HTTPException: 404 if gym not found
    """
    gym = session.exec(
        select(Gym).where(Gym.slug == slug).where(Gym.is_active == True)  # noqa: E712
    ).first()

    if not gym:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {"slug": slug},
            },
        )

    return gym


@gym_router.put(
    "/{gym_id}/profile",
    response_model=GymPublic,
    dependencies=[RequireOwnerOrManager],
)
def update_gym_profile(
    gym_id: str,
    profile_data: GymProfileUpdate,
    session: SessionDep,
    _current_staff: StaffGymDep,
) -> Gym:
    """Update gym profile information (Story 2.2, AC #1, #4, #5).

    Requires owner or manager role.

    Args:
        gym_id: UUID of the gym
        profile_data: Profile fields to update
        session: Database session
        current_staff: Authenticated staff (validated for gym access)

    Returns:
        Updated GymPublic

    Raises:
        HTTPException: 422 if invalid UUID, 404 if gym not found, 403 if unauthorized
    """
    validated_gym_id = validate_uuid(gym_id, "gym_id")
    gym = session.get(Gym, validated_gym_id)
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {},
            },
        )

    # Update only provided non-null fields (exclude_none prevents setting non-nullable to None)
    update_data = profile_data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(gym, field, value)

    session.add(gym)
    session.commit()
    session.refresh(gym)

    return gym


@gym_router.put(
    "/{gym_id}/address",
    response_model=GymPublic,
    dependencies=[RequireOwnerOrManager],
)
def update_gym_address(
    gym_id: str,
    address_data: GymAddressUpdate,
    session: SessionDep,
    _current_staff: StaffGymDep,
) -> Gym:
    """Update gym address and location (Story 2.2, AC #3).

    Requires owner or manager role.

    Args:
        gym_id: UUID of the gym
        address_data: Address fields to update
        session: Database session
        current_staff: Authenticated staff (validated for gym access)

    Returns:
        Updated GymPublic

    Raises:
        HTTPException: 422 if invalid UUID, 404 if gym not found, 403 if unauthorized
    """
    validated_gym_id = validate_uuid(gym_id, "gym_id")
    gym = session.get(Gym, validated_gym_id)
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {},
            },
        )

    # Validate coordinates are within South Africa bounds (approximately)
    # SA bounds: lat -35 to -22, lng 16 to 33
    # Validate each coordinate independently when provided
    if address_data.latitude is not None:
        if not (-35 <= address_data.latitude <= -22):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_COORDINATES",
                    "message": "Latitude must be within South Africa bounds (-35 to -22)",
                    "details": {"field": "latitude"},
                },
            )
    if address_data.longitude is not None:
        if not (16 <= address_data.longitude <= 33):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_COORDINATES",
                    "message": "Longitude must be within South Africa bounds (16 to 33)",
                    "details": {"field": "longitude"},
                },
            )

    # Update only provided non-null fields (exclude_none prevents setting non-nullable to None)
    update_data = address_data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(gym, field, value)

    session.add(gym)
    session.commit()
    session.refresh(gym)

    return gym


@gym_router.post(
    "/{gym_id}/logo",
    response_model=PhotoUploadResponse,
    dependencies=[RequireOwnerOrManager],
)
async def upload_gym_logo(
    gym_id: str,
    session: SessionDep,
    _current_staff: StaffGymDep,
    file: UploadFile = File(...),
) -> PhotoUploadResponse:
    """Upload gym logo image (Story 2.2, AC #2, #6).

    Requires owner or manager role. Validates file type (jpg, png, webp)
    and size (max 5MB).

    Args:
        gym_id: UUID of the gym
        session: Database session
        current_staff: Authenticated staff (validated for gym access)
        file: Uploaded image file

    Returns:
        PhotoUploadResponse with URL

    Raises:
        HTTPException: 422 if invalid UUID, 400 if invalid file, 404 if gym not found
    """
    validated_gym_id = validate_uuid(gym_id, "gym_id")
    gym = session.get(Gym, validated_gym_id)
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {},
            },
        )

    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_FILE_TYPE",
                "message": "File must be JPEG, PNG, or WebP",
                "details": {"allowed_types": list(ALLOWED_IMAGE_TYPES)},
            },
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "FILE_TOO_LARGE",
                "message": "File size must be less than 5MB",
                "details": {"max_size_mb": 5},
            },
        )

    # Create upload directory
    gym_upload_dir = UPLOAD_DIR / "gyms" / str(gym_id)
    gym_upload_dir.mkdir(parents=True, exist_ok=True)

    # Determine file extension
    ext = (
        file.filename.split(".")[-1]
        if file.filename and "." in file.filename
        else "jpg"
    )
    logo_path = gym_upload_dir / f"logo.{ext}"

    # Save file
    with open(logo_path, "wb") as f:
        f.write(content)

    # Update gym record
    logo_url = f"/uploads/gyms/{gym_id}/logo.{ext}"
    gym.logo_url = logo_url
    session.add(gym)
    session.commit()

    return PhotoUploadResponse(url=logo_url, message="Logo uploaded successfully")


@gym_router.post(
    "/{gym_id}/photos",
    response_model=PhotoUploadResponse,
    dependencies=[RequireOwnerOrManager],
)
async def upload_gym_photo(
    gym_id: str,
    session: SessionDep,
    _current_staff: StaffGymDep,
    file: UploadFile = File(...),
) -> PhotoUploadResponse:
    """Upload gym gallery photo (Story 2.2, AC #2, #6).

    Requires owner or manager role. Validates file type (jpg, png, webp)
    and size (max 5MB). Appends to existing photo gallery.

    Args:
        gym_id: UUID of the gym
        session: Database session
        current_staff: Authenticated staff (validated for gym access)
        file: Uploaded image file

    Returns:
        PhotoUploadResponse with URL

    Raises:
        HTTPException: 422 if invalid UUID, 400 if invalid file, 404 if gym not found
    """
    validated_gym_id = validate_uuid(gym_id, "gym_id")
    gym = session.get(Gym, validated_gym_id)
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {},
            },
        )

    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_FILE_TYPE",
                "message": "File must be JPEG, PNG, or WebP",
                "details": {"allowed_types": list(ALLOWED_IMAGE_TYPES)},
            },
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "FILE_TOO_LARGE",
                "message": "File size must be less than 5MB",
                "details": {"max_size_mb": 5},
            },
        )

    # Create upload directory
    gym_upload_dir = UPLOAD_DIR / "gyms" / str(gym_id) / "photos"
    gym_upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    ext = (
        file.filename.split(".")[-1]
        if file.filename and "." in file.filename
        else "jpg"
    )
    photo_id = str(uuid_module.uuid4())
    photo_path = gym_upload_dir / f"{photo_id}.{ext}"

    # Save file
    with open(photo_path, "wb") as f:
        f.write(content)

    # Update gym record - append to photo_urls
    photo_url = f"/uploads/gyms/{gym_id}/photos/{photo_id}.{ext}"
    current_photos = gym.photo_urls or []
    gym.photo_urls = current_photos + [photo_url]
    session.add(gym)
    session.commit()

    return PhotoUploadResponse(url=photo_url, message="Photo uploaded successfully")


@gym_router.delete(
    "/{gym_id}/photos",
    response_model=GymPublic,
    dependencies=[RequireOwnerOrManager],
)
def delete_gym_photo(
    gym_id: str,
    delete_request: GymPhotoDeleteRequest,
    session: SessionDep,
    _current_staff: StaffGymDep,
) -> Gym:
    """Delete a gym gallery photo (Story 2.2).

    Requires owner or manager role. Removes photo from gallery and deletes file.

    Args:
        gym_id: UUID of the gym
        delete_request: Contains photo_url to delete
        session: Database session
        current_staff: Authenticated staff (validated for gym access)

    Returns:
        Updated GymPublic

    Raises:
        HTTPException: 422 if invalid UUID, 400 if photo not found, 404 if gym not found
    """
    validated_gym_id = validate_uuid(gym_id, "gym_id")
    gym = session.get(Gym, validated_gym_id)
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {},
            },
        )

    # Check if photo exists in gallery
    if delete_request.photo_url not in gym.photo_urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "PHOTO_NOT_FOUND",
                "message": "Photo not found in gym gallery",
                "details": {"photo_url": delete_request.photo_url},
            },
        )

    # Remove from list
    gym.photo_urls = [url for url in gym.photo_urls if url != delete_request.photo_url]
    session.add(gym)
    session.commit()
    session.refresh(gym)

    # Try to delete file (don't fail if file doesn't exist)
    try:
        # Remove /uploads/ prefix to get relative path within UPLOAD_DIR
        relative_path = delete_request.photo_url.removeprefix("/uploads/")
        file_path = UPLOAD_DIR / relative_path
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass  # File deletion is best-effort

    return gym


@gym_router.get("/{gym_id}", response_model=GymPublic)
def get_gym(
    gym_id: str,
    session: SessionDep,
) -> Gym:
    """Get gym by ID (no auth required for public profile).

    Args:
        gym_id: UUID of the gym
        session: Database session

    Returns:
        GymPublic with all profile fields

    Raises:
        HTTPException: 422 if invalid UUID, 404 if gym not found
    """
    validated_gym_id = validate_uuid(gym_id, "gym_id")
    gym = session.get(Gym, validated_gym_id)
    if not gym or not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {},
            },
        )

    return gym
