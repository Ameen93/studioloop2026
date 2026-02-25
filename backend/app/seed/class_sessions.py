"""Seed data for ClassSession entities.

Generates realistic class schedules across all gyms for the next 14 days
plus 3 days in the past (for history testing). Sessions are assigned to
spaces and instructors based on gym configuration.
"""

from datetime import datetime, timedelta, timezone
from typing import TypedDict

from sqlmodel import Session, select

from app.models import ClassSession, Gym, Space, Staff
from app.models.class_session import ClassSessionStatus
from app.models.staff import StaffRole


class ClassDefinition(TypedDict):
    title: str
    duration_min: int
    capacity: int
    price_cents: int
    slots: list[str]


# Class types mapped to spaces and schedule patterns
CLASS_TYPES: dict[str, list[ClassDefinition]] = {
    "Main Studio": [
        {
            "title": "Morning HIIT Blast",
            "duration_min": 30,
            "capacity": 25,
            "price_cents": 0,
            "slots": ["06:00", "07:00"],
        },
        {
            "title": "Zumba Party",
            "duration_min": 50,
            "capacity": 30,
            "price_cents": 0,
            "slots": ["09:00", "18:00"],
        },
        {
            "title": "Body Pump",
            "duration_min": 45,
            "capacity": 25,
            "price_cents": 0,
            "slots": ["12:00", "17:00"],
        },
    ],
    "Spin Room": [
        {
            "title": "Spin Express",
            "duration_min": 30,
            "capacity": 20,
            "price_cents": 0,
            "slots": ["06:30", "12:30"],
        },
        {
            "title": "Endurance Ride",
            "duration_min": 45,
            "capacity": 20,
            "price_cents": 0,
            "slots": ["17:30", "18:30"],
        },
    ],
    "Yoga Studio": [
        {
            "title": "Sunrise Yoga",
            "duration_min": 60,
            "capacity": 25,
            "price_cents": 0,
            "slots": ["06:00"],
        },
        {
            "title": "Power Yoga",
            "duration_min": 60,
            "capacity": 25,
            "price_cents": 0,
            "slots": ["12:00", "17:00"],
        },
        {
            "title": "Restorative Yoga",
            "duration_min": 75,
            "capacity": 20,
            "price_cents": 0,
            "slots": ["19:00"],
        },
    ],
    "CrossFit Box": [
        {
            "title": "CrossFit WOD",
            "duration_min": 60,
            "capacity": 15,
            "price_cents": 7500,
            "slots": ["06:00", "07:00", "17:00", "18:00"],
        },
        {
            "title": "Olympic Lifting",
            "duration_min": 60,
            "capacity": 10,
            "price_cents": 10000,
            "slots": ["09:00"],
        },
    ],
    "HIIT Zone": [
        {
            "title": "Tabata Torture",
            "duration_min": 30,
            "capacity": 12,
            "price_cents": 0,
            "slots": ["06:00", "17:00"],
        },
        {
            "title": "Kettlebell Flow",
            "duration_min": 45,
            "capacity": 12,
            "price_cents": 0,
            "slots": ["12:00", "18:00"],
        },
    ],
}

# Weekend has fewer time slots
WEEKEND_SLOTS_FILTER = {"06:00", "06:30", "07:00", "12:00", "12:30"}


def seed_class_sessions(session: Session) -> int:
    """Seed class sessions for all gyms over a 17-day window.

    Creates sessions from 3 days ago through 14 days from now.
    Weekday and weekend schedules differ. Past sessions get
    varied spots_booked counts for realistic history.

    Args:
        session: SQLModel database session

    Returns:
        Number of sessions created/found
    """
    # Check if sessions already exist (idempotency)
    existing_count_result = session.exec(select(ClassSession.id)).all()
    if len(existing_count_result) > 0:
        return len(existing_count_result)

    # Load all gyms, spaces, and instructors
    gyms = session.exec(select(Gym)).all()
    all_spaces = session.exec(select(Space)).all()
    all_staff = session.exec(
        select(Staff).where(Staff.role == StaffRole.INSTRUCTOR)
    ).all()

    spaces_by_gym: dict[str, list[Space]] = {}
    for space in all_spaces:
        spaces_by_gym.setdefault(str(space.gym_id), []).append(space)

    instructors_by_gym: dict[str, list[Staff]] = {}
    for staff in all_staff:
        instructors_by_gym.setdefault(str(staff.gym_id), []).append(staff)

    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = today - timedelta(days=3)
    end_date = today + timedelta(days=14)

    count = 0

    for gym in gyms:
        gym_spaces = spaces_by_gym.get(str(gym.id), [])
        gym_instructors = instructors_by_gym.get(str(gym.id), [])
        instructor_idx = 0

        for space in gym_spaces:
            class_defs = CLASS_TYPES.get(space.name, [])
            if not class_defs:
                continue

            current_date = start_date
            while current_date < end_date:
                is_weekend = current_date.weekday() >= 5

                for class_def in class_defs:
                    for time_str in class_def["slots"]:
                        # Skip early-morning slots on weekends
                        if is_weekend and time_str in WEEKEND_SLOTS_FILTER:
                            continue

                        hour, minute = int(time_str[:2]), int(time_str[3:])
                        start_time = current_date.replace(hour=hour, minute=minute)
                        end_time = start_time + timedelta(
                            minutes=class_def["duration_min"]
                        )

                        # Assign instructor round-robin
                        instructor_id = None
                        if gym_instructors:
                            instructor_id = gym_instructors[
                                instructor_idx % len(gym_instructors)
                            ].id
                            instructor_idx += 1

                        # Past sessions: vary booking counts
                        capacity = class_def["capacity"]
                        if start_time < now:
                            # Past sessions are 50-100% full
                            spots_booked = int(capacity * (0.5 + (count % 5) * 0.1))
                            spots_booked = min(spots_booked, capacity)
                        else:
                            # Future sessions: 0-70% pre-booked
                            spots_booked = int(capacity * ((count % 7) * 0.1))
                            spots_booked = min(spots_booked, capacity)

                        status = ClassSessionStatus.SCHEDULED
                        # Cancel ~5% of past sessions
                        if start_time < now and count % 20 == 0:
                            status = ClassSessionStatus.CANCELLED

                        cs = ClassSession(
                            gym_id=gym.id,
                            space_id=space.id,
                            instructor_staff_id=instructor_id,
                            title=class_def["title"],
                            start_time=start_time,
                            end_time=end_time,
                            status=status,
                            capacity=capacity,
                            spots_booked=spots_booked,
                            price_cents=class_def["price_cents"],
                            waitlist_enabled=True,
                        )
                        session.add(cs)
                        count += 1

                current_date += timedelta(days=1)

    session.commit()
    return count
