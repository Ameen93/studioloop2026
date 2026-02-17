"""Gym model - tenant root for multi-tenancy.

The Gym model represents the tenant boundary in StudioLoop's multi-tenant
architecture. All gym-scoped data (spaces, staff, classes, etc.) is isolated
by gym_id.
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.staff import Staff


class GymBase(SQLModel):
    """Base properties shared by Gym schemas."""

    name: str = Field(
        min_length=1,
        max_length=255,
        description="Gym display name",
    )
    slug: str = Field(
        min_length=1,
        max_length=100,
        unique=True,
        index=True,
        description="URL-friendly identifier (unique across platform)",
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Gym description for marketplace listing",
    )
    tagline: str | None = Field(
        default=None,
        max_length=200,
        description="Short tagline for the gym (max 200 chars)",
    )
    is_marketplace_enabled: bool = Field(
        default=False,
        description="Whether gym participates in StudioLoop marketplace",
    )


class Gym(SoftDeleteMixin, BaseModel, GymBase, table=True):
    """Gym model - the tenant root entity.

    A Gym represents a fitness studio/gym that uses StudioLoop.
    All gym-scoped data is isolated by gym_id reference.

    Multi-Tenancy:
    - Gym is the tenant boundary
    - All gym-scoped tables have gym_id FK to this table
    - Platform-scoped data (consumers) is NOT gym-scoped
    """

    __tablename__ = "gyms"

    # Relationships
    staff: list["Staff"] = Relationship(back_populates="gym")

    # Contact information (AC #5: contact_email, contact_phone)
    contact_email: str | None = Field(
        default=None,
        max_length=255,
        description="Primary contact email for the gym",
    )
    contact_phone: str | None = Field(
        default=None,
        max_length=50,
        description="Primary contact phone (SA format: +27...)",
    )

    # Location
    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    province: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    country: str = Field(default="ZA", max_length=2, description="ISO country code")

    # Coordinates for geo search
    latitude: float | None = Field(default=None, description="GPS latitude")
    longitude: float | None = Field(default=None, description="GPS longitude")

    # Photos (Story 2.2)
    logo_url: str | None = Field(
        default=None,
        max_length=500,
        description="URL to gym logo image",
    )
    photo_urls: list[str] = Field(
        default=[],
        sa_type=JSON,
        description="List of URLs to gym gallery photos",
    )


# Schema classes for API request/response
class GymCreate(GymBase):
    """Schema for creating a new gym."""

    pass


class GymUpdate(SQLModel):
    """Schema for updating gym - all fields optional."""

    name: str | None = Field(default=None, max_length=255)
    slug: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    tagline: str | None = Field(default=None, max_length=200)
    is_marketplace_enabled: bool | None = None
    contact_email: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=50)
    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    province: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    country: str | None = Field(default=None, max_length=2)
    latitude: float | None = None
    longitude: float | None = None


class GymPublic(GymBase):
    """Schema for gym in API responses."""

    id: UUID
    contact_email: str | None = None
    contact_phone: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    province: str | None = None
    postal_code: str | None = None
    country: str = "ZA"
    latitude: float | None = None
    longitude: float | None = None
    logo_url: str | None = None
    photo_urls: list[str] = []
    is_active: bool


# =============================================================================
# Gym Profile Schemas (Story 2.2)
# =============================================================================


class GymProfileUpdate(SQLModel):
    """Schema for updating gym profile information."""

    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    tagline: str | None = Field(default=None, max_length=200)
    contact_email: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=50)


class GymAddressUpdate(SQLModel):
    """Schema for updating gym address and location."""

    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    province: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    country: str | None = Field(default=None, max_length=2)
    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
        description="GPS latitude (-90 to 90)",
    )
    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
        description="GPS longitude (-180 to 180)",
    )


class PhotoUploadResponse(SQLModel):
    """Response after successful photo upload."""

    url: str
    message: str = "Photo uploaded successfully"


class GymPhotoDeleteRequest(SQLModel):
    """Request to delete a gym photo."""

    photo_url: str = Field(description="URL of the photo to delete")


# =============================================================================
# Gym Registration Schemas (Story 2.1)
# =============================================================================


class GymRegistrationCreate(SQLModel):
    """Schema for gym owner registration.

    Creates a Consumer (role: owner), Gym, and Staff record in one operation.
    """

    # Owner details
    email: str = Field(max_length=255, description="Owner's email address")
    password: str = Field(
        min_length=8, max_length=128, description="Password (min 8 chars)"
    )
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)

    # Gym details
    gym_name: str = Field(min_length=1, max_length=255, description="Gym display name")
    gym_contact_email: str | None = Field(
        default=None,
        max_length=255,
        description="Gym contact email (defaults to owner email if not provided)",
    )
    gym_contact_phone: str | None = Field(
        default=None,
        max_length=50,
        description="Gym contact phone (SA format: +27...)",
    )


class GymRegistrationResponse(SQLModel):
    """Response after successful gym registration.

    Includes IDs for all three created records.
    """

    owner_id: UUID
    gym_id: UUID
    staff_id: UUID
    email: str
    gym_name: str
    gym_slug: str
    message: str = "Registration successful. Please verify your email."
