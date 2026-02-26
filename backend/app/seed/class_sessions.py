"""Seed data for ClassSession entities.

Generates realistic class schedules across all gyms for the next 14 days
plus 3 days in the past (for history testing). Sessions are assigned to
spaces, instructors, and class templates based on gym configuration.
"""

from datetime import datetime, timedelta, timezone
from typing import TypedDict
from uuid import UUID

from sqlmodel import Session, select

from app.models import ClassSession, ClassTemplate, Gym, Space, Staff
from app.models.class_session import ApprovalStatus, ClassSessionStatus
from app.models.class_template import ClassType
from app.models.staff import StaffRole


class ClassDefinition(TypedDict):
    title: str
    duration_min: int
    capacity: int
    price_cents: int
    slots: list[str]
    class_type: ClassType


CLASS_TYPES: dict[str, list[ClassDefinition]] = {
    "Main Studio": [
        {
            "title": "Morning HIIT Blast",
            "duration_min": 30,
            "capacity": 25,
            "price_cents": 0,
            "slots": ["06:00", "07:00"],
            "class_type": ClassType.HIIT,
        },
        {
            "title": "Zumba Party",
            "duration_min": 50,
            "capacity": 30,
            "price_cents": 0,
            "slots": ["09:00", "18:00"],
            "class_type": ClassType.DANCE,
        },
        {
            "title": "Body Pump",
            "duration_min": 45,
            "capacity": 25,
            "price_cents": 0,
            "slots": ["12:00", "17:00"],
            "class_type": ClassType.STRENGTH,
        },
    ],
    "Spin Room": [
        {
            "title": "Spin Express",
            "duration_min": 30,
            "capacity": 20,
            "price_cents": 0,
            "slots": ["06:30", "12:30"],
            "class_type": ClassType.CYCLING,
        },
        {
            "title": "Endurance Ride",
            "duration_min": 45,
            "capacity": 20,
            "price_cents": 0,
            "slots": ["17:30", "18:30"],
            "class_type": ClassType.CYCLING,
        },
    ],
    "Yoga Studio": [
        {
            "title": "Sunrise Yoga",
            "duration_min": 60,
            "capacity": 25,
            "price_cents": 0,
            "slots": ["06:00"],
            "class_type": ClassType.YOGA,
        },
        {
            "title": "Power Yoga",
            "duration_min": 60,
            "capacity": 25,
            "price_cents": 0,
            "slots": ["12:00", "17:00"],
            "class_type": ClassType.YOGA,
        },
        {
            "title": "Restorative Yoga",
            "duration_min": 75,
            "capacity": 20,
            "price_cents": 0,
            "slots": ["19:00"],
            "class_type": ClassType.YOGA,
        },
    ],
    "CrossFit Box": [
        {
            "title": "CrossFit WOD",
            "duration_min": 60,
            "capacity": 15,
            "price_cents": 7500,
            "slots": ["06:00", "07:00", "17:00", "18:00"],
            "class_type": ClassType.CROSSFIT,
        },
        {
            "title": "Olympic Lifting",
            "duration_min": 60,
            "capacity": 10,
            "price_cents": 10000,
            "slots": ["09:00"],
            "class_type": ClassType.CROSSFIT,
        },
    ],
    "HIIT Zone": [
        {
            "title": "Tabata Torture",
            "duration_min": 30,
            "capacity": 12,
            "price_cents": 0,
            "slots": ["06:00", "17:00"],
            "class_type": ClassType.HIIT,
        },
        {
            "title": "Kettlebell Flow",
            "duration_min": 45,
            "capacity": 12,
            "price_cents": 0,
            "slots": ["12:00", "18:00"],
            "class_type": ClassType.STRENGTH,
        },
    ],
}

WEEKEND_SLOTS_FILTER = {"06:00", "06:30", "07:00", "12:00", "12:30"}


def seed_class_sessions(session: Session) -> int:
    """Seed class sessions for all gyms over a 17-day window."""
    existing_count_result = session.exec(select(ClassSession.id)).all()
    if len(existing_count_result) > 0:
        return len(existing_count_result)

    gyms = session.exec(select(Gym)).all()
    all_spaces = session.exec(select(Space)).all()
    all_staff = session.exec(
        select(Staff).where(Staff.role == StaffRole.INSTRUCTOR)
    ).all()
    all_templates = session.exec(select(ClassTemplate)).all()

    spaces_by_gym: dict[str, list[Space]] = {}
    for space in all_spaces:
        spaces_by_gym.setdefault(str(space.gym_id), []).append(space)

    instructors_by_gym: dict[str, list[Staff]] = {}
    for staff in all_staff:
        instructors_by_gym.setdefault(str(staff.gym_id), []).append(staff)

    # Build template lookup: (gym_id, name) -> template
    template_lookup: dict[tuple[str, str], ClassTemplate] = {}
    for t in all_templates:
        template_lookup[(str(t.gym_id), t.name)] = t

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
                        if is_weekend and time_str in WEEKEND_SLOTS_FILTER:
                            continue

                        hour, minute = int(time_str[:2]), int(time_str[3:])
                        start_time = current_date.replace(hour=hour, minute=minute)
                        end_time = start_time + timedelta(
                            minutes=class_def["duration_min"]
                        )

                        instructor_id = None
                        if gym_instructors:
                            instructor_id = gym_instructors[
                                instructor_idx % len(gym_instructors)
                            ].id
                            instructor_idx += 1

                        capacity = class_def["capacity"]
                        if start_time < now:
                            spots_booked = int(capacity * (0.5 + (count % 5) * 0.1))
                            spots_booked = min(spots_booked, capacity)
                        else:
                            spots_booked = int(capacity * ((count % 7) * 0.1))
                            spots_booked = min(spots_booked, capacity)

                        status = ClassSessionStatus.SCHEDULED
                        if start_time < now and count % 20 == 0:
                            status = ClassSessionStatus.CANCELLED

                        # Find matching template
                        template = template_lookup.get(
                            (str(gym.id), class_def["title"])
                        )
                        template_id: UUID | None = template.id if template else None

                        cs = ClassSession(
                            gym_id=gym.id,
                            space_id=space.id,
                            instructor_staff_id=instructor_id,
                            title=class_def["title"],
                            class_type=class_def["class_type"],
                            start_time=start_time,
                            end_time=end_time,
                            status=status,
                            capacity=capacity,
                            spots_booked=spots_booked,
                            price_cents=class_def["price_cents"],
                            waitlist_enabled=True,
                            waitlist_capacity=5,
                            class_template_id=template_id,
                            approval_status=ApprovalStatus.AUTO_APPROVED,
                            marketplace_visible=True,
                        )
                        session.add(cs)
                        count += 1

                current_date += timedelta(days=1)

    session.commit()
    return count
