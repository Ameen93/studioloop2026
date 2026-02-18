from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Field

from app.models.base import GymScopedModel


class DigitalWaiverAcceptance(GymScopedModel, table=True):
    __tablename__ = "digital_waiver_acceptances"

    consumer_id: UUID = Field(foreign_key="consumers.id", nullable=False, index=True)
    gym_membership_id: UUID = Field(foreign_key="gym_memberships.id", nullable=False, index=True)
    accepted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    waiver_version: str = Field(default="v1", max_length=50)
