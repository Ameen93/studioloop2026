"""Seed data for Booking entities.

Creates realistic bookings linking consumers to class sessions.
Includes a mix of past bookings (checked-in, cancelled) and
future bookings (confirmed, waiting) for testing all flows.
"""

from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models import Booking, ClassSession, Consumer
from app.models.booking import BookingSource, BookingStatus, BookingType
from app.models.class_session import ClassSessionStatus


def seed_bookings(session: Session) -> int:
    """Seed bookings across consumers and sessions.

    - Past scheduled sessions: consumers get checked_in or cancelled bookings
    - Future sessions: consumers get confirmed bookings
    - Mix of direct and marketplace sources

    Args:
        session: SQLModel database session

    Returns:
        Number of bookings created/found
    """
    existing = session.exec(select(Booking.id)).all()
    if len(existing) > 0:
        return len(existing)

    consumers = session.exec(select(Consumer)).all()
    if not consumers:
        return 0

    # Get scheduled sessions only (skip cancelled ones)
    sessions_list = session.exec(
        select(ClassSession).where(ClassSession.status == ClassSessionStatus.SCHEDULED)
    ).all()
    if not sessions_list:
        return 0

    now = datetime.now(timezone.utc)
    count = 0

    for i, cs in enumerate(sessions_list):
        # Book 2-5 consumers per session
        num_bookings = 2 + (i % 4)

        for j in range(num_bookings):
            consumer = consumers[(i + j) % len(consumers)]
            # Handle both naive and aware datetimes from DB
            cs_start = (
                cs.start_time.replace(tzinfo=timezone.utc)
                if cs.start_time.tzinfo is None
                else cs.start_time
            )
            is_past = cs_start < now

            if is_past:
                # Past sessions: 70% checked in, 20% cancelled, 10% booked (no-show)
                roll = (i + j) % 10
                if roll < 7:
                    status = BookingStatus.CHECKED_IN
                    checked_in_at = cs_start
                elif roll < 9:
                    status = BookingStatus.CANCELLED
                    checked_in_at = None
                else:
                    status = BookingStatus.BOOKED
                    checked_in_at = None
            else:
                # Future sessions: all confirmed
                status = BookingStatus.BOOKED
                checked_in_at = None

            # Alternate between direct and marketplace bookings
            source = (
                BookingSource.MARKETPLACE if (i + j) % 5 == 0 else BookingSource.DIRECT
            )
            booking_type = (
                BookingType.PAY_PER_CLASS
                if cs.price_cents > 0
                else BookingType.MEMBERSHIP_BENEFIT
            )

            cancelled_at = cs_start if status == BookingStatus.CANCELLED else None

            booking = Booking(
                gym_id=cs.gym_id,
                consumer_id=consumer.id,
                session_id=cs.id,
                booking_type=booking_type,
                source=source,
                status=status,
                price_paid_cents=cs.price_cents
                if booking_type == BookingType.PAY_PER_CLASS
                else None,
                cancelled_at=cancelled_at,
                checked_in_at=checked_in_at,
            )
            session.add(booking)
            count += 1

    session.commit()
    return count
