"""Seed data for MarketplaceSubscription entities.

Creates marketplace subscriptions for consumers who book across
multiple gyms. Mix of plan tiers with realistic usage patterns.
"""

from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.models import Consumer, MarketplaceSubscription
from app.models.marketplace_subscription import (
    MarketplacePlanTier,
    MarketplaceSubscriptionStatus,
)


def seed_marketplace_subscriptions(session: Session) -> int:
    """Seed marketplace subscriptions idempotently.

    ~40% of consumers get a marketplace subscription:
    - 50% on EIGHT tier (8 classes/month)
    - 30% on TWELVE tier (12 classes/month)
    - 20% on UNLIMITED tier
    - Mix of ACTIVE, PAUSED, and CANCELLED statuses

    Args:
        session: SQLModel database session

    Returns:
        Number of subscriptions created/found
    """
    existing = session.exec(select(MarketplaceSubscription.id)).all()
    if len(existing) > 0:
        return len(existing)

    consumers = session.exec(select(Consumer)).all()
    if not consumers:
        return 0

    now = datetime.now(timezone.utc)
    count = 0

    # ~40% of consumers get marketplace subscriptions
    for i, consumer in enumerate(consumers):
        if i % 5 >= 2:  # skip 60%
            continue

        # Tier distribution
        tier_roll = i % 10
        if tier_roll < 5:
            tier = MarketplacePlanTier.EIGHT
            classes_total = 8
        elif tier_roll < 8:
            tier = MarketplacePlanTier.TWELVE
            classes_total = 12
        else:
            tier = MarketplacePlanTier.UNLIMITED
            classes_total = 999  # effectively unlimited

        # Status: 70% active, 15% paused, 15% cancelled
        status_roll = i % 20
        if status_roll < 14:
            status = MarketplaceSubscriptionStatus.ACTIVE
            paused_at = None
            cancelled_at = None
        elif status_roll < 17:
            status = MarketplaceSubscriptionStatus.PAUSED
            paused_at = now - timedelta(days=(i * 3) % 14)
            cancelled_at = None
        else:
            status = MarketplaceSubscriptionStatus.CANCELLED
            paused_at = None
            cancelled_at = now - timedelta(days=(i * 5) % 30)

        # Remaining classes based on usage
        if tier == MarketplacePlanTier.UNLIMITED:
            classes_remaining = 999
        elif status == MarketplaceSubscriptionStatus.ACTIVE:
            classes_remaining = max(0, classes_total - (i % (classes_total + 1)))
        else:
            classes_remaining = classes_total  # paused/cancelled = no usage

        reset_at = now - timedelta(days=(i * 7) % 28)

        sub = MarketplaceSubscription(
            consumer_id=consumer.id,
            plan_tier=tier,
            classes_total=classes_total,
            classes_remaining=classes_remaining,
            reset_at=reset_at,
            status=status,
            paused_at=paused_at,
            cancelled_at=cancelled_at,
        )
        session.add(sub)
        count += 1

    session.commit()
    return count
