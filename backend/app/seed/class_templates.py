"""Seed data for ClassTemplate entities.

Creates realistic class templates for each gym with varied class types,
colors, and default configurations.
"""

from typing import TYPE_CHECKING, Any

from sqlmodel import Session, select

from app.models import ClassTemplate, Space, Staff
from app.models.class_template import ClassType
from app.models.staff import StaffRole

if TYPE_CHECKING:
    from app.models import Gym

TEMPLATE_DEFS: list[dict[str, Any]] = [
    {
        "name": "Morning HIIT Blast",
        "class_type": ClassType.HIIT,
        "default_duration_minutes": 30,
        "default_capacity": 25,
        "default_price_cents": 0,
        "color": "#EF4444",
        "space_name": "Main Studio",
    },
    {
        "name": "Zumba Party",
        "class_type": ClassType.DANCE,
        "default_duration_minutes": 50,
        "default_capacity": 30,
        "default_price_cents": 0,
        "color": "#F59E0B",
        "space_name": "Main Studio",
    },
    {
        "name": "Body Pump",
        "class_type": ClassType.STRENGTH,
        "default_duration_minutes": 45,
        "default_capacity": 25,
        "default_price_cents": 0,
        "color": "#8B5CF6",
        "space_name": "Main Studio",
    },
    {
        "name": "Spin Express",
        "class_type": ClassType.CYCLING,
        "default_duration_minutes": 30,
        "default_capacity": 20,
        "default_price_cents": 0,
        "color": "#06B6D4",
        "space_name": "Spin Room",
    },
    {
        "name": "Endurance Ride",
        "class_type": ClassType.CYCLING,
        "default_duration_minutes": 45,
        "default_capacity": 20,
        "default_price_cents": 0,
        "color": "#0EA5E9",
        "space_name": "Spin Room",
    },
    {
        "name": "Sunrise Yoga",
        "class_type": ClassType.YOGA,
        "default_duration_minutes": 60,
        "default_capacity": 25,
        "default_price_cents": 0,
        "color": "#10B981",
        "space_name": "Yoga Studio",
    },
    {
        "name": "Power Yoga",
        "class_type": ClassType.YOGA,
        "default_duration_minutes": 60,
        "default_capacity": 25,
        "default_price_cents": 0,
        "color": "#34D399",
        "space_name": "Yoga Studio",
    },
    {
        "name": "CrossFit WOD",
        "class_type": ClassType.CROSSFIT,
        "default_duration_minutes": 60,
        "default_capacity": 15,
        "default_price_cents": 7500,
        "color": "#F97316",
        "space_name": "CrossFit Box",
    },
    {
        "name": "Boxing Fundamentals",
        "class_type": ClassType.BOXING,
        "default_duration_minutes": 45,
        "default_capacity": 12,
        "default_price_cents": 5000,
        "color": "#DC2626",
        "space_name": "HIIT Zone",
    },
    {
        "name": "Pilates Core",
        "class_type": ClassType.PILATES,
        "default_duration_minutes": 50,
        "default_capacity": 20,
        "default_price_cents": 0,
        "color": "#EC4899",
        "space_name": "Yoga Studio",
    },
]


def seed_class_templates(session: Session, gyms: list["Gym"]) -> int:
    """Seed class templates for all gyms.

    Returns:
        Number of templates created/found
    """
    existing = session.exec(select(ClassTemplate.id)).all()
    if len(existing) > 0:
        return len(existing)

    all_spaces = session.exec(select(Space)).all()
    all_staff = session.exec(
        select(Staff).where(Staff.role == StaffRole.INSTRUCTOR)
    ).all()

    spaces_by_gym: dict[str, dict[str, Space]] = {}
    for gym_space in all_spaces:
        spaces_by_gym.setdefault(str(gym_space.gym_id), {})[gym_space.name] = gym_space

    instructors_by_gym: dict[str, list[Staff]] = {}
    for staff in all_staff:
        instructors_by_gym.setdefault(str(staff.gym_id), []).append(staff)

    count = 0
    for gym in gyms:
        gym_spaces = spaces_by_gym.get(str(gym.id), {})
        gym_instructors = instructors_by_gym.get(str(gym.id), [])
        instructor_idx = 0

        for tdef in TEMPLATE_DEFS:
            template_space = gym_spaces.get(tdef["space_name"])
            if not template_space:
                continue

            instructor_id = None
            if gym_instructors:
                instructor_id = gym_instructors[
                    instructor_idx % len(gym_instructors)
                ].id
                instructor_idx += 1

            template = ClassTemplate(
                gym_id=gym.id,
                name=tdef["name"],
                class_type=tdef["class_type"],
                default_duration_minutes=tdef["default_duration_minutes"],
                default_capacity=tdef["default_capacity"],
                default_price_cents=tdef["default_price_cents"],
                color=tdef["color"],
                default_space_id=template_space.id,
                default_instructor_staff_id=instructor_id,
                waitlist_enabled=True,
            )
            session.add(template)
            count += 1

    session.commit()
    return count
