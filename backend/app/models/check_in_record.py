from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID

from sqlmodel import Field

from app.models.base import GymScopedModel


class CheckInSource(StrEnum):
    QR = "qr"
    MANUAL = "manual"
    OFFLINE_QR = "offline_qr"


class CheckInRecord(GymScopedModel, table=True):
    __tablename__ = "check_in_records"

    consumer_id: UUID = Field(foreign_key="consumers.id", nullable=False, index=True)
    booking_id: UUID | None = Field(default=None, foreign_key="bookings.id", index=True)
    source: CheckInSource = Field(default=CheckInSource.MANUAL, max_length=20)
    checked_in_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    offline_recorded_at: datetime | None = Field(default=None)
    synced_at: datetime | None = Field(default=None)
