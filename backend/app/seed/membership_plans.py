"""Seed data for MembershipPlan entities.

DEFERRED: MembershipPlan model will be created in Epic 4 (Membership Plans & Consumer Enrollment).

This module is a placeholder that documents the planned membership plan
seed data structure for when the model becomes available.

Planned Membership Plans (per gym):
- Basic: R299/month, 8 classes per month
- Premium: R499/month, unlimited classes
- Unlimited: R699/month, unlimited classes + priority booking + guest passes

Each gym will have their own variations of these plans with
potentially different pricing based on location and amenities.
"""

from typing import TYPE_CHECKING

from sqlmodel import Session

if TYPE_CHECKING:
    from app.models import Gym


# Documented for future implementation
PLANNED_MEMBERSHIP_PLANS = [
    {
        "name": "Basic",
        "description": "Perfect for getting started with fitness",
        "price_zar": 299.00,
        "billing_period": "monthly",
        "class_limit": 8,
        "features": ["Access to all classes", "Booking up to 24h in advance"],
    },
    {
        "name": "Premium",
        "description": "For dedicated fitness enthusiasts",
        "price_zar": 499.00,
        "billing_period": "monthly",
        "class_limit": None,  # Unlimited
        "features": [
            "Unlimited classes",
            "Booking up to 7 days in advance",
            "10% merchandise discount",
        ],
    },
    {
        "name": "Unlimited",
        "description": "The ultimate fitness experience",
        "price_zar": 699.00,
        "billing_period": "monthly",
        "class_limit": None,  # Unlimited
        "features": [
            "Unlimited classes",
            "Priority booking",
            "2 guest passes per month",
            "20% merchandise discount",
            "Free locker",
        ],
    },
]


def seed_membership_plans(_session: Session, _gyms: list["Gym"]) -> int:
    """Seed membership plans for each gym.

    DEFERRED: Returns 0 until MembershipPlan model is created in Epic 4.

    Planned implementation:
    - Create Basic, Premium, Unlimited plans for each gym
    - Adjust pricing slightly per gym based on location
    - Set up billing periods and class limits

    Args:
        session: SQLModel database session
        gyms: List of Gym objects to create plans for

    Returns:
        Number of plans created (currently 0)
    """
    # TODO: Implement when MembershipPlan model is created in Epic 4
    # See Epic 4: Membership Plans & Consumer Enrollment for model definition

    return 0
