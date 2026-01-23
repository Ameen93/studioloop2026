# ruff: noqa: T201
"""Seed orchestrator - manages seed order and dependencies.

Handles the correct ordering of seed operations to respect
foreign key constraints:
1. Gyms (no dependencies)
2. Consumers (no dependencies)
3. Spaces (depends on Gyms)
4. Staff (depends on Gyms) - DEFERRED
5. Membership Plans (depends on Gyms) - DEFERRED
6. Class Templates (depends on Gyms) - DEFERRED
7. Class Sessions (depends on Class Templates) - DEFERRED
8. Bookings (depends on Sessions, Consumers) - DEFERRED
"""

from sqlmodel import Session, delete

from app.models import Consumer, Gym, Space

# Placeholder imports for future models
from app.seed.bookings import seed_bookings
from app.seed.class_sessions import seed_class_sessions
from app.seed.class_templates import seed_class_templates

# Import seed functions (will be created in subsequent tasks)
from app.seed.consumers import seed_consumers
from app.seed.gyms import seed_gyms
from app.seed.membership_plans import seed_membership_plans
from app.seed.spaces import seed_spaces
from app.seed.staff import seed_staff


def seed_all(session: Session) -> dict[str, int]:
    """Seed all data in dependency order.

    Returns a summary dict with counts of each entity type seeded.
    All operations are idempotent - running twice won't create duplicates.

    Args:
        session: SQLModel database session

    Returns:
        Dictionary mapping entity names to counts created/found
    """
    summary: dict[str, int] = {}

    # Phase 1: Independent entities
    print("Phase 1: Seeding independent entities...")

    gyms = seed_gyms(session)
    summary["gyms"] = len(gyms)
    print(f"  - Gyms: {len(gyms)}")

    consumers = seed_consumers(session)
    summary["consumers"] = len(consumers)
    print(f"  - Consumers: {len(consumers)}")

    # Phase 2: Gym-dependent entities
    print("\nPhase 2: Seeding gym-dependent entities...")

    spaces = seed_spaces(session, gyms)
    summary["spaces"] = len(spaces)
    print(f"  - Spaces: {len(spaces)}")

    # Phase 3: Deferred entities (models not yet created)
    print("\nPhase 3: Deferred entities (models not ready)...")

    staff_count = seed_staff(session, gyms)
    summary["staff"] = staff_count
    print(f"  - Staff: {staff_count} (deferred to Epic 3)")

    plans_count = seed_membership_plans(session, gyms)
    summary["membership_plans"] = plans_count
    print(f"  - Membership Plans: {plans_count} (deferred to Epic 4)")

    templates_count = seed_class_templates(session, gyms)
    summary["class_templates"] = templates_count
    print(f"  - Class Templates: {templates_count} (deferred to Epic 5)")

    sessions_count = seed_class_sessions(session)
    summary["class_sessions"] = sessions_count
    print(f"  - Class Sessions: {sessions_count} (deferred to Epic 5)")

    bookings_count = seed_bookings(session)
    summary["bookings"] = bookings_count
    print(f"  - Bookings: {bookings_count} (deferred to Epic 6)")

    return summary


def reset_seed_data(session: Session) -> None:
    """Delete all seed data in reverse dependency order.

    CAUTION: This deletes ALL data from seeded tables, not just
    the specific seed records. Use with care in shared environments.

    Deletion order (respects foreign key constraints):
    1. Bookings (depends on sessions, consumers)
    2. Class Sessions (depends on templates)
    3. Class Templates (depends on gyms)
    4. Membership Plans (depends on gyms)
    5. Staff (depends on gyms)
    6. Spaces (depends on gyms)
    7. Consumers (independent)
    8. Gyms (independent)

    Args:
        session: SQLModel database session
    """
    print("Deleting seed data in reverse dependency order...")

    # Note: Deferred models don't exist yet, but we include the pattern
    # for when they are created. The delete will simply do nothing if
    # the table doesn't exist.

    # Delete gym-scoped children first
    print("  - Deleting Spaces...")
    session.exec(delete(Space))  # type: ignore[call-overload]

    # Delete independent entities
    print("  - Deleting Consumers...")
    session.exec(delete(Consumer))  # type: ignore[call-overload]

    print("  - Deleting Gyms...")
    session.exec(delete(Gym))  # type: ignore[call-overload]

    session.commit()
    print("Reset complete.")
