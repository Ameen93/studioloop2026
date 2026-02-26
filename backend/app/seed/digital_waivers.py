"""Seed data for DigitalWaiverAcceptance entities.

Creates waiver acceptances for consumers who have active gym memberships.
In a real system, consumers sign a waiver when they first join a gym.
"""

from datetime import timedelta, timezone

from sqlmodel import Session, select

from app.models import DigitalWaiverAcceptance, GymMembership
from app.models.gym_membership import GymMembershipStatus


def seed_digital_waivers(session: Session) -> int:
    """Seed digital waiver acceptances idempotently.

    Every active or inactive gym membership gets a signed waiver.
    Cancelled memberships: 80% have signed waivers (some cancelled early).
    Waiver accepted_at is always shortly after membership started_at.

    Args:
        session: SQLModel database session

    Returns:
        Number of waivers created/found
    """
    existing = session.exec(select(DigitalWaiverAcceptance.id)).all()
    if len(existing) > 0:
        return len(existing)

    memberships = session.exec(select(GymMembership)).all()
    if not memberships:
        return 0

    count = 0

    for i, membership in enumerate(memberships):
        # Skip some cancelled memberships (20% didn't sign)
        if membership.status == GymMembershipStatus.CANCELLED and i % 5 == 0:
            continue

        # Waiver signed shortly after membership start
        started = membership.started_at
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        accepted_at = started + timedelta(minutes=5 + (i % 30))

        waiver = DigitalWaiverAcceptance(
            gym_id=membership.gym_id,
            consumer_id=membership.consumer_id,
            gym_membership_id=membership.id,
            accepted_at=accepted_at,
            waiver_version="v1" if i % 3 != 0 else "v2",
        )
        session.add(waiver)
        count += 1

    session.commit()
    return count
