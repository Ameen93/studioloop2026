"""Seed data for ClassTemplate entities.

DEFERRED: ClassTemplate model will be created in Epic 5 (Class Scheduling System).

This module is a placeholder that documents the planned class template
seed data structure for when the model becomes available.

Planned Class Templates:
- Yoga: 60 min, capacity 20, calm intensity
- Spin: 45 min, capacity 15, high intensity
- HIIT: 30 min, capacity 25, very high intensity
- CrossFit: 60 min, capacity 12, very high intensity
- Pilates: 55 min, capacity 18, moderate intensity
- Boxing: 45 min, capacity 16, high intensity
- Zumba: 50 min, capacity 30, moderate intensity
"""

from typing import TYPE_CHECKING

from sqlmodel import Session

if TYPE_CHECKING:
    from app.models import Gym


# Documented for future implementation
PLANNED_CLASS_TEMPLATES = [
    {
        "name": "Yoga",
        "description": "Mindful movement combining breathwork, flexibility, and strength poses.",
        "duration_minutes": 60,
        "default_capacity": 20,
        "intensity_level": "low",
        "equipment_needed": ["Yoga mat", "Blocks (optional)", "Strap (optional)"],
        "calories_estimate": 200,
    },
    {
        "name": "Spin",
        "description": "High-energy indoor cycling with music-driven intervals.",
        "duration_minutes": 45,
        "default_capacity": 15,
        "intensity_level": "high",
        "equipment_needed": ["Spin bike (provided)", "Heart rate monitor (optional)"],
        "calories_estimate": 500,
    },
    {
        "name": "HIIT",
        "description": "High-Intensity Interval Training for maximum calorie burn.",
        "duration_minutes": 30,
        "default_capacity": 25,
        "intensity_level": "very_high",
        "equipment_needed": ["Mat", "Dumbbells (optional)"],
        "calories_estimate": 400,
    },
    {
        "name": "CrossFit",
        "description": "Functional fitness combining weightlifting, cardio, and gymnastics.",
        "duration_minutes": 60,
        "default_capacity": 12,
        "intensity_level": "very_high",
        "equipment_needed": ["Barbell", "Kettlebells", "Pull-up bar"],
        "calories_estimate": 600,
    },
    {
        "name": "Pilates",
        "description": "Core-focused workout improving posture, flexibility, and body awareness.",
        "duration_minutes": 55,
        "default_capacity": 18,
        "intensity_level": "moderate",
        "equipment_needed": ["Mat", "Reformer (if available)"],
        "calories_estimate": 250,
    },
    {
        "name": "Boxing",
        "description": "Full-body cardio workout with boxing techniques and bag work.",
        "duration_minutes": 45,
        "default_capacity": 16,
        "intensity_level": "high",
        "equipment_needed": ["Boxing gloves", "Hand wraps"],
        "calories_estimate": 450,
    },
    {
        "name": "Zumba",
        "description": "Dance fitness party with Latin and international music.",
        "duration_minutes": 50,
        "default_capacity": 30,
        "intensity_level": "moderate",
        "equipment_needed": [],
        "calories_estimate": 350,
    },
]


def seed_class_templates(_session: Session, _gyms: list["Gym"]) -> int:
    """Seed class templates for each gym.

    DEFERRED: Returns 0 until ClassTemplate model is created in Epic 5.

    Planned implementation:
    - Create standard templates for common class types
    - Associate templates with gyms based on their facilities
    - Set default pricing for marketplace gyms

    Args:
        session: SQLModel database session
        gyms: List of Gym objects to create templates for

    Returns:
        Number of templates created (currently 0)
    """
    # TODO: Implement when ClassTemplate model is created in Epic 5
    # See Epic 5: Class Scheduling System for model definition

    return 0
