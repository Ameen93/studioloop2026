"""Seed data for MembershipPlan entities.

Creates three tiers of membership plans per gym with SA pricing in ZAR.
Prices stored in cents (e.g. R299 = 29900).
"""

from typing import Any

from sqlmodel import Session, select

from app.models import Gym, MembershipPlan
from app.models.gym_membership import GymMembershipTier
from app.models.membership_plan import MembershipBillingCycle

# Base plans — prices adjusted per gym below
PLAN_TEMPLATES: list[dict[str, Any]] = [
    {
        "name": "Basic",
        "description": "Perfect for getting started — 8 classes per month with standard booking.",
        "base_price_cents": 29900,  # R299
        "billing_cycle": MembershipBillingCycle.MONTHLY,
        "tier": GymMembershipTier.BASIC,
        "benefits": [
            "8 classes per month",
            "Booking up to 24h in advance",
            "Access to all standard classes",
        ],
        "usage_limits": {"classes_per_month": 8, "advance_booking_days": 1},
        "rules": {"cancellation_hours": 4, "no_show_penalty": False},
    },
    {
        "name": "Premium",
        "description": "For dedicated fitness enthusiasts — unlimited classes and priority features.",
        "base_price_cents": 49900,  # R499
        "billing_cycle": MembershipBillingCycle.MONTHLY,
        "tier": GymMembershipTier.PREMIUM,
        "benefits": [
            "Unlimited classes",
            "Booking up to 7 days in advance",
            "10% merchandise discount",
            "Free towel service",
        ],
        "usage_limits": {"classes_per_month": -1, "advance_booking_days": 7},
        "rules": {"cancellation_hours": 2, "no_show_penalty": True},
    },
    {
        "name": "Unlimited",
        "description": "The ultimate fitness experience — everything included with VIP perks.",
        "base_price_cents": 69900,  # R699
        "billing_cycle": MembershipBillingCycle.MONTHLY,
        "tier": GymMembershipTier.UNLIMITED,
        "benefits": [
            "Unlimited classes",
            "Priority booking",
            "2 guest passes per month",
            "20% merchandise discount",
            "Free locker",
            "Free parking",
        ],
        "usage_limits": {
            "classes_per_month": -1,
            "advance_booking_days": 14,
            "guest_passes_per_month": 2,
        },
        "rules": {"cancellation_hours": 1, "no_show_penalty": False},
    },
]

# Price multipliers per gym (premium locations charge more)
GYM_PRICE_MULTIPLIER: dict[str, float] = {
    "fitzone-sandton": 1.15,  # Sandton premium
    "oxygen-cape-town": 1.10,  # Sea Point premium
    "pure-energy-pretoria": 1.00,
    "sweat-box-durban": 0.95,
    "crossfit-centurion": 1.05,
}


def seed_membership_plans(session: Session, gyms: list[Gym]) -> int:
    """Seed membership plans for each gym idempotently.

    Each gym gets Basic, Premium, and Unlimited plans with
    location-adjusted pricing.

    Args:
        session: SQLModel database session
        gyms: List of Gym objects to create plans for

    Returns:
        Number of plans created/found
    """
    count = 0

    for gym in gyms:
        multiplier = GYM_PRICE_MULTIPLIER.get(gym.slug, 1.0)

        for template in PLAN_TEMPLATES:
            existing = session.exec(
                select(MembershipPlan).where(
                    MembershipPlan.gym_id == gym.id,
                    MembershipPlan.name == template["name"],
                )
            ).first()
            if existing:
                count += 1
                continue

            adjusted_price = int(template["base_price_cents"] * multiplier)

            plan = MembershipPlan(
                gym_id=gym.id,
                name=template["name"],
                description=template["description"],
                price_cents=adjusted_price,
                billing_cycle=template["billing_cycle"],
                tier=template["tier"],
                benefits=template["benefits"],
                usage_limits=template["usage_limits"],
                rules=template["rules"],
            )
            session.add(plan)
            count += 1

    session.commit()
    return count
