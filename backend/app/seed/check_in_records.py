"""Seed data for CheckInRecord entities.

Creates check-in records for bookings that have CHECKED_IN status.
In a real system, check-ins happen when a consumer scans their QR code
or a staff member manually checks them in at the front desk.
"""

from datetime import timedelta, timezone

from sqlmodel import Session, select

from app.models import Booking, CheckInRecord
from app.models.booking import BookingStatus
from app.models.check_in_record import CheckInSource


def seed_check_in_records(session: Session) -> int:
    """Seed check-in records for checked-in bookings idempotently.

    Source distribution:
    - 60% QR code scans (self-service)
    - 30% manual check-ins (front desk)
    - 10% offline QR (synced later)

    Args:
        session: SQLModel database session

    Returns:
        Number of check-in records created/found
    """
    existing = session.exec(select(CheckInRecord.id)).all()
    if len(existing) > 0:
        return len(existing)

    # Get all checked-in bookings
    checked_in_bookings = session.exec(
        select(Booking).where(Booking.status == BookingStatus.CHECKED_IN)
    ).all()
    if not checked_in_bookings:
        return 0

    count = 0

    for i, booking in enumerate(checked_in_bookings):
        # Source distribution: 60% QR, 30% manual, 10% offline
        roll = i % 10
        if roll < 6:
            source = CheckInSource.QR
        elif roll < 9:
            source = CheckInSource.MANUAL
        else:
            source = CheckInSource.OFFLINE_QR

        checked_in_at = booking.checked_in_at
        if checked_in_at and checked_in_at.tzinfo is None:
            checked_in_at = checked_in_at.replace(tzinfo=timezone.utc)

        # Offline QR records have a delayed sync
        offline_recorded_at = None
        synced_at = None
        if source == CheckInSource.OFFLINE_QR and checked_in_at:
            offline_recorded_at = checked_in_at
            synced_at = checked_in_at + timedelta(hours=1 + (i % 4))

        record = CheckInRecord(
            gym_id=booking.gym_id,
            consumer_id=booking.consumer_id,
            booking_id=booking.id,
            source=source,
            checked_in_at=checked_in_at,
            offline_recorded_at=offline_recorded_at,
            synced_at=synced_at,
        )
        session.add(record)
        count += 1

    session.commit()
    return count
