"""Consumer model - platform-scoped identity.

Consumers are platform-owned users who book classes at gyms.
Unlike gym-scoped data, consumers are NOT isolated by gym_id
because they can book at multiple gyms.
"""

from uuid import UUID

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from app.models.base import BaseModel, SoftDeleteMixin


class ConsumerBase(SQLModel):
    """Base properties shared by Consumer schemas."""

    email: EmailStr = Field(
        unique=True,
        index=True,
        max_length=255,
        description="Consumer email (unique across platform)",
    )
    full_name: str | None = Field(
        default=None,
        max_length=255,
        description="Consumer full name",
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
class ConsumerCreate(ConsumerBase):
    """Schema for consumer registration."""

    password: str = Field(min_length=8, max_length=128)


class ConsumerUpdate(SQLModel):
    """Schema for updating consumer profile - all fields optional."""

    full_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    avatar_url: str | None = Field(default=None, max_length=500)
    accepts_marketing: bool | None = None


class ConsumerPublic(ConsumerBase):
    """Schema for consumer in API responses."""

    id: UUID
    avatar_url: str | None = None
    is_email_verified: bool
    is_active: bool
