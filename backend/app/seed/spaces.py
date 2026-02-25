"""Seed data for Space entities.

Creates realistic gym spaces/studios for each seeded gym.
Spaces are gym-scoped and demonstrate the multi-tenancy pattern.
"""

from typing import Any

from sqlmodel import Session, select

from app.models import Gym, Space

# Space templates - each gym will get a selection of these
SPACE_TEMPLATES: list[dict[str, Any]] = [
    {
        "name": "Main Studio",
        "description": "Large open studio space suitable for group classes like aerobics, dance, and circuit training.",
        "capacity": 30,
        "floor_area_sqm": 150.0,
        "has_mirrors": True,
        "has_sound_system": True,
        "has_air_conditioning": True,
        "is_bookable": True,
    },
    {
        "name": "Spin Room",
        "description": "Dedicated cycling studio with premium spin bikes and immersive lighting.",
        "capacity": 20,
        "floor_area_sqm": 80.0,
        "has_mirrors": False,
        "has_sound_system": True,
        "has_air_conditioning": True,
        "is_bookable": True,
    },
    {
        "name": "Yoga Studio",
        "description": "Tranquil space designed for yoga, pilates, and meditation with natural lighting.",
        "capacity": 25,
        "floor_area_sqm": 100.0,
        "has_mirrors": True,
        "has_sound_system": True,
        "has_air_conditioning": True,
        "is_bookable": True,
    },
    {
        "name": "CrossFit Box",
        "description": "Industrial-style functional fitness area with rigs, platforms, and rubber flooring.",
        "capacity": 15,
        "floor_area_sqm": 200.0,
        "has_mirrors": False,
        "has_sound_system": True,
        "has_air_conditioning": False,  # Natural ventilation
        "is_bookable": True,
    },
    {
        "name": "HIIT Zone",
        "description": "High-intensity training area with battle ropes, kettlebells, and plyometric equipment.",
        "capacity": 12,
        "floor_area_sqm": 60.0,
        "has_mirrors": True,
        "has_sound_system": True,
        "has_air_conditioning": True,
        "is_bookable": True,
    },
]

# Which spaces each gym should have (by gym slug -> space names)
GYM_SPACE_ASSIGNMENTS: dict[str, list[str]] = {
    "fitzone-sandton": ["Main Studio", "Spin Room", "Yoga Studio", "HIIT Zone"],
    "oxygen-cape-town": ["Main Studio", "Yoga Studio", "Spin Room"],
    "pure-energy-pretoria": ["Main Studio", "Spin Room", "HIIT Zone"],
    "sweat-box-durban": ["Main Studio", "HIIT Zone"],
    "crossfit-centurion": ["CrossFit Box", "HIIT Zone"],
}


def seed_spaces(session: Session, gyms: list[Gym]) -> list[Space]:
    """Seed spaces for each gym idempotently.

    Each gym gets a predefined set of spaces based on their focus.
    Spaces are checked by (gym_id, name) combination for idempotency.

    Args:
        session: SQLModel database session
        gyms: List of Gym objects to create spaces for

    Returns:
        List of all seeded/existing Space objects
    """
    spaces: list[Space] = []

    # Create lookup dict for space templates
    template_by_name = {t["name"]: t for t in SPACE_TEMPLATES}

    for gym in gyms:
        # Get assigned space names for this gym
        assigned_spaces = GYM_SPACE_ASSIGNMENTS.get(gym.slug, ["Main Studio"])

        for space_name in assigned_spaces:
            template = template_by_name.get(space_name)
            if not template:
                continue

            # Check if space already exists for this gym
            existing = session.exec(
                select(Space).where(
                    Space.gym_id == gym.id,
                    Space.name == space_name,
                )
            ).first()

            if existing:
                spaces.append(existing)
                continue

            # Create new space with gym_id
            space_data = {**template, "gym_id": gym.id}
            space = Space(**space_data)
            session.add(space)
            spaces.append(space)

    session.commit()

    return spaces
