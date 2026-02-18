from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID

from sqlmodel import Field

from app.models.base import GymScopedModel


class WaitlistStatus(StrEnum):
    WAITLISTED = "waitlisted"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    EXPIRED = "expired"


class WaitlistEntry(GymScopedModel, table=True):
    __tablename__ = "waitlist_entries"

    consumer_id: UUID = Field(foreign_key="consumers.id", nullable=False, index=True)
    session_id: UUID = Field(foreign_key="class_sessions.id", nullable=False, index=True)
    position: int = Field(ge=1)
    status: WaitlistStatus = Field(default=WaitlistStatus.WAITLISTED, max_length=20)
    offered_at: datetime | None = Field(default=None)
    expires_at: datetime | None = Field(default=None)
    accepted_at: datetime | None = Field(default=None)

    def offer(self, expires_at: datetime) -> None:
        self.status = WaitlistStatus.OFFERED
        self.offered_at = datetime.now(timezone.utc)
        self.expires_at = expires_at

    def accept(self) -> None:
        self.status = WaitlistStatus.ACCEPTED
        self.accepted_at = datetime.now(timezone.utc)

    def expire(self) -> None:
        self.status = WaitlistStatus.EXPIRED
