from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID

from sqlmodel import Field

from app.models.base import GymScopedModel


class BookingType(StrEnum):
    MEMBERSHIP_BENEFIT = "membership_benefit"
    PAY_PER_CLASS = "pay_per_class"


class BookingStatus(StrEnum):
    BOOKED = "booked"
    CANCELLED = "cancelled"
    CHECKED_IN = "checked_in"


class BookingSource(StrEnum):
    DIRECT = "direct"
    MARKETPLACE = "marketplace"


class Booking(GymScopedModel, table=True):
    __tablename__ = "bookings"

    consumer_id: UUID = Field(foreign_key="consumers.id", nullable=False, index=True)
    session_id: UUID = Field(foreign_key="class_sessions.id", nullable=False, index=True)
    gym_membership_id: UUID | None = Field(default=None, foreign_key="gym_memberships.id", index=True)
    booking_type: BookingType = Field(default=BookingType.MEMBERSHIP_BENEFIT, max_length=32)
    source: BookingSource = Field(default=BookingSource.DIRECT, max_length=20)
    status: BookingStatus = Field(default=BookingStatus.BOOKED, max_length=20)
    price_paid_cents: int | None = Field(default=None, ge=0)
    cancelled_at: datetime | None = Field(default=None)
    checked_in_at: datetime | None = Field(default=None)
    cancellation_refunded: bool = Field(default=False)

    def mark_cancelled(self) -> None:
        self.status = BookingStatus.CANCELLED
        self.cancelled_at = datetime.now(timezone.utc)

    def mark_checked_in(self) -> None:
        self.status = BookingStatus.CHECKED_IN
        self.checked_in_at = datetime.now(timezone.utc)
