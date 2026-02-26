"""Seed data for GymClosure entities.

Creates realistic gym closure dates using South African public holidays
and ad-hoc maintenance/event closures per gym.
"""

from datetime import date

from sqlmodel import Session, select

from app.models import Gym, GymClosure

# 2026 SA public holidays + common closure reasons
SA_PUBLIC_HOLIDAYS_2026: list[tuple[date, str]] = [
    (date(2026, 1, 1), "New Year's Day"),
    (date(2026, 3, 21), "Human Rights Day"),
    (date(2026, 4, 3), "Good Friday"),
    (date(2026, 4, 6), "Family Day"),
    (date(2026, 4, 27), "Freedom Day"),
    (date(2026, 5, 1), "Workers' Day"),
    (date(2026, 6, 16), "Youth Day"),
    (date(2026, 8, 9), "National Women's Day"),
    (date(2026, 8, 10), "National Women's Day (observed)"),
    (date(2026, 9, 24), "Heritage Day"),
    (date(2026, 12, 16), "Day of Reconciliation"),
    (date(2026, 12, 25), "Christmas Day"),
    (date(2026, 12, 26), "Day of Goodwill"),
]

# Ad-hoc closures per gym slug (maintenance, events, etc.)
GYM_SPECIFIC_CLOSURES: dict[str, list[tuple[date, str]]] = {
    "fitzone-sandton": [
        (date(2026, 2, 14), "Equipment maintenance day"),
        (date(2026, 3, 7), "Staff training day"),
        (date(2026, 7, 18), "Annual deep clean"),
    ],
    "oxygen-cape-town": [
        (date(2026, 1, 2), "Extended New Year closure"),
        (date(2026, 4, 18), "Cape Town Cycle Tour day"),
        (date(2026, 6, 20), "Plumbing maintenance"),
    ],
    "pure-energy-pretoria": [
        (date(2026, 3, 14), "Facility upgrade"),
        (date(2026, 8, 15), "Air conditioning repair"),
    ],
    "sweat-box-durban": [
        (date(2026, 7, 11), "Comrades Marathon support day"),
        (date(2026, 11, 1), "Annual fumigation"),
    ],
    "crossfit-centurion": [
        (date(2026, 5, 16), "Competition prep — members only event"),
        (date(2026, 9, 12), "Equipment delivery and setup"),
    ],
}


def seed_gym_closures(session: Session, gyms: list[Gym]) -> int:
    """Seed gym closure dates idempotently.

    Each gym gets:
    - All SA public holidays as closures
    - 2-3 gym-specific maintenance/event closures

    Args:
        session: SQLModel database session
        gyms: List of Gym objects

    Returns:
        Number of closures created/found
    """
    count = 0

    for gym in gyms:
        # Add public holidays for all gyms
        all_closures = list(SA_PUBLIC_HOLIDAYS_2026)

        # Add gym-specific closures
        specific = GYM_SPECIFIC_CLOSURES.get(gym.slug, [])
        all_closures.extend(specific)

        # Existing DB closures for this gym
        existing_dates = {
            closure_date
            for closure_date in session.exec(
                select(GymClosure.closure_date).where(GymClosure.gym_id == gym.id)
            ).all()
        }

        # Track dates seen during this run as well (prevents duplicate adds before flush)
        seen_dates = set(existing_dates)

        for closure_date, reason in all_closures:
            if closure_date in seen_dates:
                count += 1
                continue

            closure = GymClosure(
                gym_id=gym.id,
                closure_date=closure_date,
                reason=reason,
            )
            session.add(closure)
            seen_dates.add(closure_date)
            count += 1

    session.commit()
    return count
