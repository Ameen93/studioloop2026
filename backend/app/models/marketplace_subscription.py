from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID

from sqlmodel import Field

from app.models.base import BaseModel


class MarketplacePlanTier(StrEnum):
    EIGHT = "eight"
    TWELVE = "twelve"
    UNLIMITED = "unlimited"


class MarketplaceSubscriptionStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class MarketplaceSubscription(BaseModel, table=True):
    __tablename__ = "marketplace_subscriptions"

    consumer_id: UUID = Field(foreign_key="consumers.id", nullable=False, index=True)
    plan_tier: MarketplacePlanTier = Field(default=MarketplacePlanTier.EIGHT, max_length=20)
    classes_total: int = Field(default=8, ge=0)
    classes_remaining: int = Field(default=8, ge=0)
    reset_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: MarketplaceSubscriptionStatus = Field(default=MarketplaceSubscriptionStatus.ACTIVE, max_length=20)
    paused_at: datetime | None = Field(default=None)
    cancelled_at: datetime | None = Field(default=None)
    downgrade_to_tier: MarketplacePlanTier | None = Field(default=None, max_length=20)


class ReferralInvite(BaseModel, table=True):
    __tablename__ = "referral_invites"

    referrer_consumer_id: UUID = Field(foreign_key="consumers.id", nullable=False, index=True)
    referral_code: str = Field(min_length=4, max_length=64, index=True)
    channel: str = Field(default="copy_link", max_length=32)
    class_session_id: UUID | None = Field(default=None, foreign_key="class_sessions.id", index=True)
    referred_email_hash: str | None = Field(default=None, max_length=128)
    signed_up_consumer_id: UUID | None = Field(default=None, foreign_key="consumers.id", index=True)
    signed_up_at: datetime | None = Field(default=None)
