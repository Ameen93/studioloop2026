"""Seed data for WaitlistEntry entities.

Creates waitlist entries for future class sessions that are at or near
capacity. Simulates consumers waiting for spots to open up.
"""

from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.models import ClassSession, Consumer, WaitlistEntry
from app.models.class_session import ClassSessionStatus
from app.models.waitlist_entry import WaitlistStatus


def seed_waitlist_entries(session: Session) -> int:
    """Seed waitlist entries for full/near-full sessions idempotently.

    Targets future sessions where spots_booked >= capacity - 1.
    Each full session gets 1-3 waitlist entries.
    Status mix: 60% WAITLISTED, 20% OFFERED, 10% ACCEPTED, 10% EXPIRED

    Args:
        session: SQLModel database session

    Returns:
        Number of waitlist entries created/found
    """
    existing = session.exec(select(WaitlistEntry.id)).all()
    if len(existing) > 0:
        return len(existing)

    now = datetime.now(timezone.utc)

    # Find future sessions that are full or nearly full
    full_sessions = session.exec(
        select(ClassSession).where(
            ClassSession.status == ClassSessionStatus.SCHEDULED,
            ClassSession.start_time > now,
            ClassSession.waitlist_enabled == True,  # noqa: E712
        )
    ).all()

    # Filter to sessions at/near capacity
    full_sessions = [
        s for s in full_sessions if s.capacity > 0 and s.spots_booked >= s.capacity - 1
    ]

    if not full_sessions:
        return 0

    consumers = session.exec(select(Consumer)).all()
    if not consumers:
        return 0

    count = 0

    for i, cs in enumerate(full_sessions):
        # 1-3 waitlist entries per full session
        num_entries = 1 + (i % 3)

        for j in range(num_entries):
            # Pick a consumer not already booked (approximate — use index offset)
            consumer = consumers[(i * 3 + j + 7) % len(consumers)]

            position = j + 1

            # Status distribution
            roll = (i + j) % 10
            if roll < 6:
                status = WaitlistStatus.WAITLISTED
                offered_at = None
                expires_at = None
                accepted_at = None
            elif roll < 8:
                status = WaitlistStatus.OFFERED
                offered_at = now - timedelta(hours=(i % 12) + 1)
                expires_at = offered_at + timedelta(hours=24)
                accepted_at = None
            elif roll == 8:
                status = WaitlistStatus.ACCEPTED
                offered_at = now - timedelta(hours=(i % 24) + 2)
                expires_at = offered_at + timedelta(hours=24)
                accepted_at = offered_at + timedelta(hours=(i % 6) + 1)
            else:
                status = WaitlistStatus.EXPIRED
                offered_at = now - timedelta(days=2)
                expires_at = offered_at + timedelta(hours=24)
                accepted_at = None

            entry = WaitlistEntry(
                gym_id=cs.gym_id,
                consumer_id=consumer.id,
                session_id=cs.id,
                position=position,
                status=status,
                offered_at=offered_at,
                expires_at=expires_at,
                accepted_at=accepted_at,
            )
            session.add(entry)
            count += 1

    session.commit()
    return count
