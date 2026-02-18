from enum import StrEnum
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from app.models.base import BaseModel, SoftDeleteMixin


class GymMembershipStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class GymMembershipTier(StrEnum):
    BASIC = "basic"
    PREMIUM = "premium"
    UNLIMITED = "unlimited"


class GymMembership(SoftDeleteMixin, BaseModel, table=True):
    __tablename__ = "gym_memberships"
    __table_args__ = (UniqueConstraint("gym_id", "consumer_id", name="uq_gym_membership_gym_consumer"),)

    gym_id: UUID = Field(foreign_key="gyms.id", nullable=False, index=True)
    consumer_id: UUID = Field(foreign_key="consumers.id", nullable=False, index=True)
    membership_tier: GymMembershipTier = Field(default=GymMembershipTier.BASIC, max_length=20)
    status: GymMembershipStatus = Field(default=GymMembershipStatus.ACTIVE, max_length=20)
