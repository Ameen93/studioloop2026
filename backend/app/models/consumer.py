"""Consumer model - platform-scoped identity.

Consumers are platform-owned users who book classes at gyms.
Unlike gym-scoped data, consumers are NOT isolated by gym_id
because they can book at multiple gyms.
"""

from enum import Enum
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from app.models.base import BaseModel, SoftDeleteMixin


class UserRole(str, Enum):
    """User roles for platform access control (ARCH-13).

    Consumers have the 'consumer' role by default.
    Staff roles (owner, manager, etc.) are assigned when joining a gym.
    """

    CONSUMER = "consumer"
    OWNER = "owner"
    MANAGER = "manager"
    FRONT_DESK = "front_desk"
    INSTRUCTOR = "instructor"


class ConsumerBase(SQLModel):
    """Base properties shared by Consumer schemas."""

    email: EmailStr = Field(
        unique=True,
        index=True,
        max_length=255,
        description="Consumer email (unique across platform)",
    )
    first_name: str = Field(
        max_length=100,
        description="Consumer first name",
    )
    last_name: str = Field(
        max_length=100,
        description="Consumer last name",
    )
    phone: str | None = Field(
        default=None,
        max_length=50,
        index=True,
        description="Phone number (SA format: +27...)",
    )


class Consumer(SoftDeleteMixin, BaseModel, ConsumerBase, table=True):
    """Consumer model - platform-scoped user identity.

    Consumers are platform-owned (NOT gym-scoped) because:
    - A consumer can book classes at multiple gyms
    - Consumer identity is shared across the marketplace
    - Bookings link consumers to gyms via gym_id

    POPIA Compliance:
    - Consumers can request account deletion
    - Soft-delete preserves audit trail
    - Personal data can be anonymized
    """

    __tablename__ = "consumers"

    # Role for access control (ARCH-13)
    role: UserRole = Field(
        default=UserRole.CONSUMER,
        description="User role for access control",
    )

    # Authentication (if using separate from User model)
    hashed_password: str | None = Field(
        default=None,
        description="Hashed password (null if social login only)",
    )

    # Profile
    avatar_url: str | None = Field(
        default=None,
        max_length=500,
        description="Profile picture URL",
    )

    # Legacy full_name field (kept for backward compatibility)
    full_name: str | None = Field(
        default=None,
        max_length=255,
        description="Full name (deprecated, use first_name + last_name)",
    )

    # Verification status
    is_email_verified: bool = Field(
        default=False,
        description="Whether email has been verified",
    )
    is_phone_verified: bool = Field(
        default=False,
        description="Whether phone has been verified",
    )

    # Marketing preferences (POPIA compliance)
    accepts_marketing: bool = Field(
        default=False,
        description="Consent to receive marketing communications",
    )

    # Relationships (to be populated as domain models are created)
    # bookings: list["Booking"] = Relationship(back_populates="consumer")
    # memberships: list["Membership"] = Relationship(back_populates="consumer")


# Schema classes for API request/response
class ConsumerCreate(SQLModel):
    """Schema for consumer registration."""

    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=50)


class ConsumerUpdate(SQLModel):
    """Schema for updating consumer profile - all fields optional."""

    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=50)
    avatar_url: str | None = Field(default=None, max_length=500)
    accepts_marketing: bool | None = None


class ConsumerPublic(SQLModel):
    """Schema for consumer in API responses."""

    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None = None
    role: UserRole
    avatar_url: str | None = None
    is_email_verified: bool
    is_active: bool
