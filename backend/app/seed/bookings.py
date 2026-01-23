"""Seed data for Booking entities.

DEFERRED: Booking model will be created in Epic 6 (Booking & Check-in).

This module is a placeholder that documents the planned booking
seed data structure for when the model becomes available.

Planned Bookings:
- Mix of confirmed, checked-in, cancelled, and no-show bookings
- Some bookings in the past (for history testing)
- Some bookings in the future (for check-in testing)
- Include waitlist entries for popular classes
- Various booking sources (direct, marketplace)
"""

from sqlmodel import Session

# Documented for future implementation
PLANNED_BOOKING_STATUSES = [
    "confirmed",  # Booking confirmed, awaiting class
    "checked_in",  # Consumer attended the class
    "cancelled",  # Consumer cancelled before class
    "no_show",  # Consumer didn't attend
    "waitlisted",  # On waitlist for full class
]

PLANNED_BOOKING_SOURCES = [
    "direct",  # Booked directly at gym
    "marketplace",  # Booked via StudioLoop marketplace
    "walk_in",  # Walk-in booking at reception
]


def seed_bookings(_session: Session) -> int:
    """Seed sample bookings.

    DEFERRED: Returns 0 until Booking model is created in Epic 6.

    Planned implementation:
    - Create bookings linking consumers to class sessions
    - Mix of booking statuses (confirmed, checked_in, cancelled)
    - Include past bookings for testing history views
    - Include future bookings for testing check-in flows
    - Create some waitlist entries for full classes

    Args:
        session: SQLModel database session

    Returns:
        Number of bookings created (currently 0)
    """
    # TODO: Implement when Booking model is created in Epic 6
    # See Epic 6: Booking & Check-in for model definition

    return 0
