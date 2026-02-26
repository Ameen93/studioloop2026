# ruff: noqa: T201
"""Seed orchestrator - manages seed order and dependencies.

Handles the correct ordering of seed operations to respect
foreign key constraints:

Phase 1 (Independent):
  1. Gyms (no dependencies)
  2. Consumers (no dependencies)

Phase 2 (Gym-dependent):
  3. Spaces (depends on Gyms)
  4. Staff (depends on Gyms)
  5. Membership Plans (depends on Gyms)
  6. Gym Closures (depends on Gyms)

Phase 3 (Multi-dependency):
  7. Class Templates (no-op, kept for interface compat)
  8. Class Sessions (depends on Gyms, Spaces, Staff)
  9. Gym Memberships (depends on Consumers, Gyms, Membership Plans)
  10. Marketplace Subscriptions (depends on Consumers)

Phase 4 (Booking & post-booking):
  11. Bookings (depends on Sessions, Consumers)
  12. Digital Waivers (depends on Gym Memberships)
  13. Check-in Records (depends on Bookings)
  14. Payments (depends on Gym Memberships, Bookings)
  15. Waitlist Entries (depends on Class Sessions, Consumers)
  16. Notifications (depends on Bookings, Consumers, Gyms)
"""

from sqlalchemy import text
from sqlmodel import Session

from app.seed.bookings import seed_bookings
from app.seed.check_in_records import seed_check_in_records
from app.seed.class_sessions import seed_class_sessions
from app.seed.class_templates import seed_class_templates
from app.seed.consumers import seed_consumers
from app.seed.digital_waivers import seed_digital_waivers
from app.seed.gym_closures import seed_gym_closures
from app.seed.gym_memberships import seed_gym_memberships
from app.seed.gyms import seed_gyms
from app.seed.marketplace_subscriptions import seed_marketplace_subscriptions
from app.seed.membership_plans import seed_membership_plans
from app.seed.notifications import seed_notifications
from app.seed.payments import seed_payments
from app.seed.spaces import seed_spaces
from app.seed.staff import seed_staff
from app.seed.waitlist_entries import seed_waitlist_entries


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

    staff_count = seed_staff(session, gyms)
    summary["staff"] = staff_count
    print(f"  - Staff: {staff_count}")

    plans_count = seed_membership_plans(session, gyms)
    summary["membership_plans"] = plans_count
    print(f"  - Membership Plans: {plans_count}")

    closures_count = seed_gym_closures(session, gyms)
    summary["gym_closures"] = closures_count
    print(f"  - Gym Closures: {closures_count}")

    # Phase 3: Multi-dependency entities
    print("\nPhase 3: Seeding schedule, memberships, and subscriptions...")

    templates_count = seed_class_templates(session, gyms)
    summary["class_templates"] = templates_count
    if templates_count > 0:
        print(f"  - Class Templates: {templates_count}")

    sessions_count = seed_class_sessions(session)
    summary["class_sessions"] = sessions_count
    print(f"  - Class Sessions: {sessions_count}")

    memberships_count = seed_gym_memberships(session)
    summary["gym_memberships"] = memberships_count
    print(f"  - Gym Memberships: {memberships_count}")

    marketplace_count = seed_marketplace_subscriptions(session)
    summary["marketplace_subscriptions"] = marketplace_count
    print(f"  - Marketplace Subscriptions: {marketplace_count}")

    # Phase 4: Booking & post-booking entities
    print("\nPhase 4: Seeding bookings and related data...")

    bookings_count = seed_bookings(session)
    summary["bookings"] = bookings_count
    print(f"  - Bookings: {bookings_count}")

    waivers_count = seed_digital_waivers(session)
    summary["digital_waivers"] = waivers_count
    print(f"  - Digital Waivers: {waivers_count}")

    checkins_count = seed_check_in_records(session)
    summary["check_in_records"] = checkins_count
    print(f"  - Check-in Records: {checkins_count}")

    payments_count = seed_payments(session)
    summary["payments"] = payments_count
    print(f"  - Payments: {payments_count}")

    waitlist_count = seed_waitlist_entries(session)
    summary["waitlist_entries"] = waitlist_count
    print(f"  - Waitlist Entries: {waitlist_count}")

    notifications_count = seed_notifications(session)
    summary["notifications"] = notifications_count
    print(f"  - Notifications: {notifications_count}")

    return summary


def reset_seed_data(session: Session) -> None:
    """Delete all seed data safely for tests.

    CAUTION: This truncates all public tables except `alembic_version`.
    Intended for test/local reset workflows.
    """
    print("Deleting seed data in reverse dependency order...")

    # Limit reset scope to seed-related tables so we don't collide with
    # global test fixture transactions (e.g. auth/user reads in session fixtures).
    seed_tables = [
        "notifications",
        "waitlist_entries",
        "payments",
        "payment_receipts",
        "payment_webhook_events",
        "check_in_records",
        "digital_waiver_acceptances",
        "bookings",
        "marketplace_subscriptions",
        "gym_memberships",
        "class_sessions",
        "class_templates",
        "membership_plans",
        "gym_closures",
        "gym_messages",
        "notification_preferences",
        "notification_templates",
        "referral_invites",
        "spaces",
        "staff",
        "consumers",
        "gyms",
    ]

    existing_rows = session.execute(
        text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
    ).all()

    existing = {row if isinstance(row, str) else row[0] for row in existing_rows}
    table_names = [name for name in seed_tables if name in existing]

    if table_names:
        quoted = ", ".join(f'"{name}"' for name in table_names)
        print(f"  - Truncating {len(table_names)} seed tables...")
        session.execute(text("SET LOCAL lock_timeout = '5s'"))
        session.execute(text(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE"))

    session.commit()
    print("Reset complete.")
