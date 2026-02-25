"""Seed data for GymMembership entities.

Links consumers to gyms with membership plans. Distributes consumers
across gyms so each gym has a realistic member base with a mix of
active, inactive, and cancelled memberships at different tiers.
"""

from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.models import Consumer, Gym, GymMembership, MembershipPlan
from app.models.gym_membership import GymMembershipStatus, GymMembershipTier


def seed_gym_memberships(session: Session) -> int:
    """Seed gym memberships linking consumers to gyms idempotently.

    Distribution:
    - Each consumer gets 1-3 memberships across different gyms
    - ~70% ACTIVE, ~15% CANCELLED, ~15% INACTIVE
    - Tier matches the linked membership plan
    - Some consumers have memberships at multiple gyms

    Args:
        session: SQLModel database session

    Returns:
        Number of gym memberships created/found
    """
    existing = session.exec(select(GymMembership.id)).all()
    if len(existing) > 0:
        return len(existing)

    consumers = session.exec(select(Consumer)).all()
    gyms = session.exec(select(Gym)).all()
    if not consumers or not gyms:
        return 0

    # Build lookup: gym_id -> list of plans (sorted by tier for predictability)
    plans_by_gym: dict[str, list[MembershipPlan]] = {}
    all_plans = session.exec(select(MembershipPlan)).all()
    for plan in all_plans:
        gym_id_str = str(plan.gym_id)
        if gym_id_str not in plans_by_gym:
            plans_by_gym[gym_id_str] = []
        plans_by_gym[gym_id_str].append(plan)

    now = datetime.now(timezone.utc)
    count = 0

    # Assign consumers to gyms — spread them around
    # Consumer 0-4 → gym 0 (primary), some also get gym 1
    # Consumer 5-9 → gym 1, some also get gym 2
    # etc.
    for i, consumer in enumerate(consumers):
        # Primary gym membership (everyone gets one)
        primary_gym = gyms[i % len(gyms)]
        plans = plans_by_gym.get(str(primary_gym.id), [])
        if not plans:
            continue

        # Pick tier based on consumer index for variety
        tier_idx = i % 3  # 0=Basic, 1=Premium, 2=Unlimited
        plan = plans[tier_idx % len(plans)]
        tier = [
            GymMembershipTier.BASIC,
            GymMembershipTier.PREMIUM,
            GymMembershipTier.UNLIMITED,
        ][tier_idx]

        # Status distribution: 70% active, 15% cancelled, 15% inactive
        roll = i % 20
        if roll < 14:
            status = GymMembershipStatus.ACTIVE
            started_at = now - timedelta(days=30 + (i * 17) % 180)
            ended_at = None
        elif roll < 17:
            status = GymMembershipStatus.CANCELLED
            started_at = now - timedelta(days=90 + (i * 13) % 120)
            ended_at = now - timedelta(days=(i * 7) % 30)
        else:
            status = GymMembershipStatus.INACTIVE
            started_at = now - timedelta(days=60 + (i * 11) % 90)
            ended_at = now - timedelta(days=(i * 5) % 15)

        membership = GymMembership(
            gym_id=primary_gym.id,
            consumer_id=consumer.id,
            membership_plan_id=plan.id,
            membership_tier=tier,
            status=status,
            payment_method_last4=str(1000 + i * 111)[-4:],
            started_at=started_at,
            ended_at=ended_at,
        )
        session.add(membership)
        count += 1

        # ~40% of consumers also get a second gym membership (marketplace users)
        if i % 5 < 2:
            secondary_gym = gyms[(i + 2) % len(gyms)]
            if secondary_gym.id == primary_gym.id:
                secondary_gym = gyms[(i + 3) % len(gyms)]

            sec_plans = plans_by_gym.get(str(secondary_gym.id), [])
            if sec_plans:
                sec_plan = sec_plans[0]  # Basic at secondary gym
                membership2 = GymMembership(
                    gym_id=secondary_gym.id,
                    consumer_id=consumer.id,
                    membership_plan_id=sec_plan.id,
                    membership_tier=GymMembershipTier.BASIC,
                    status=GymMembershipStatus.ACTIVE,
                    payment_method_last4=str(2000 + i * 222)[-4:],
                    started_at=now - timedelta(days=15 + (i * 9) % 60),
                    ended_at=None,
                )
                session.add(membership2)
                count += 1

    session.commit()
    return count
