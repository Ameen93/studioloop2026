"""Gym model - tenant root for multi-tenancy.

The Gym model represents the tenant boundary in StudioLoop's multi-tenant
architecture. All gym-scoped data (spaces, staff, classes, etc.) is isolated
by gym_id.
"""

from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import BaseModel, SoftDeleteMixin


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

    # Relationships (to be populated as domain models are created)
    # spaces: list["Space"] = Relationship(back_populates="gym")
    # staff: list["Staff"] = Relationship(back_populates="gym")

    # Contact information
    email: str | None = Field(
        default=None,
        max_length=255,
        description="Primary contact email",
    )
    phone: str | None = Field(
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


# Schema classes for API request/response
class GymCreate(GymBase):
    """Schema for creating a new gym."""

    pass


class GymUpdate(SQLModel):
    """Schema for updating gym - all fields optional."""

    name: str | None = Field(default=None, max_length=255)
    slug: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    is_marketplace_enabled: bool | None = None
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
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
    email: str | None = None
    phone: str | None = None
    city: str | None = None
    province: str | None = None
    is_active: bool
