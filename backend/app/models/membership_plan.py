from enum import StrEnum
from uuid import UUID

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.models.base import GymScopedSoftDeleteModel
from app.models.gym_membership import GymMembershipTier


class MembershipBillingCycle(StrEnum):
    MONTHLY = "monthly"
    WEEKLY = "weekly"


class MembershipPlan(GymScopedSoftDeleteModel, table=True):
    __tablename__ = "membership_plans"

    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    price_cents: int = Field(default=0, ge=0)
    billing_cycle: MembershipBillingCycle = Field(
        default=MembershipBillingCycle.MONTHLY, max_length=20
    )
    tier: GymMembershipTier = Field(default=GymMembershipTier.BASIC, max_length=20)
    benefits: list[str] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )
    usage_limits: dict[str, int | bool | str] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    rules: dict[str, int | bool | str] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    waiver_text: str | None = Field(default=None, max_length=5000)


class MembershipPlanCreate(SQLModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    price_cents: int = Field(default=0, ge=0)
    billing_cycle: MembershipBillingCycle = Field(
        default=MembershipBillingCycle.MONTHLY
    )
    tier: GymMembershipTier = Field(default=GymMembershipTier.BASIC)


class MembershipPlanUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    price_cents: int | None = Field(default=None, ge=0)
    billing_cycle: MembershipBillingCycle | None = None
    tier: GymMembershipTier | None = None
    benefits: list[str] | None = None
    usage_limits: dict[str, int | bool | str] | None = None
    rules: dict[str, int | bool | str] | None = None
    waiver_text: str | None = Field(default=None, max_length=5000)


class MembershipPlanPublic(SQLModel):
    id: UUID
    gym_id: UUID
    name: str
    description: str | None
    price_cents: int
    billing_cycle: MembershipBillingCycle
    tier: GymMembershipTier
    benefits: list[str]
    usage_limits: dict[str, int | bool | str]
    rules: dict[str, int | bool | str]
    waiver_text: str | None
    is_active: bool
