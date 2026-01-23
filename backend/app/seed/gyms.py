"""Seed data for Gym entities.

Creates realistic South African gym data for testing purposes.
All gyms use actual SA cities, provinces, and realistic coordinates.
"""

# South African gym seed data
# Coordinates are approximate real locations in each city
from typing import Any

from sqlmodel import Session, select

from app.models import Gym

SEED_GYMS: list[dict[str, Any]] = [
    {
        "name": "FitZone Sandton",
        "slug": "fitzone-sandton",
        "description": "Premium fitness center in the heart of Sandton with state-of-the-art equipment and expert trainers.",
        "is_marketplace_enabled": True,
        "email": "info@fitzone-sandton.co.za",
        "phone": "+27 11 784 5632",
        "address_line1": "123 Rivonia Road",
        "address_line2": "Sandton City Mall",
        "city": "Johannesburg",
        "province": "Gauteng",
        "postal_code": "2196",
        "country": "ZA",
        "latitude": -26.1076,
        "longitude": 28.0567,
    },
    {
        "name": "Oxygen Fitness Cape Town",
        "slug": "oxygen-cape-town",
        "description": "Breathe life into your fitness journey at our stunning Sea Point location with ocean views.",
        "is_marketplace_enabled": True,
        "email": "hello@oxygenfitness.co.za",
        "phone": "+27 21 434 8901",
        "address_line1": "45 Beach Road",
        "address_line2": "Sea Point Promenade",
        "city": "Cape Town",
        "province": "Western Cape",
        "postal_code": "8005",
        "country": "ZA",
        "latitude": -33.9172,
        "longitude": 18.3859,
    },
    {
        "name": "Pure Energy Pretoria",
        "slug": "pure-energy-pretoria",
        "description": "Unleash your potential at Pretoria's most energetic fitness studio.",
        "is_marketplace_enabled": True,
        "email": "admin@pureenergy.co.za",
        "phone": "+27 12 346 7890",
        "address_line1": "78 Brooklyn Road",
        "address_line2": "Brooklyn Mall",
        "city": "Pretoria",
        "province": "Gauteng",
        "postal_code": "0181",
        "country": "ZA",
        "latitude": -25.7715,
        "longitude": 28.2381,
    },
    {
        "name": "The Sweat Box Durban",
        "slug": "sweat-box-durban",
        "description": "High-intensity training in Durban's premier boutique fitness studio.",
        "is_marketplace_enabled": True,
        "email": "sweat@thesweatbox.co.za",
        "phone": "+27 31 572 3456",
        "address_line1": "22 Florida Road",
        "address_line2": "Morningside",
        "city": "Durban",
        "province": "KwaZulu-Natal",
        "postal_code": "4001",
        "country": "ZA",
        "latitude": -29.8350,
        "longitude": 31.0178,
    },
    {
        "name": "CrossFit Centurion",
        "slug": "crossfit-centurion",
        "description": "Forge your strength at Centurion's original CrossFit affiliate box.",
        "is_marketplace_enabled": False,  # Not on marketplace
        "email": "wod@crossfitcenturion.co.za",
        "phone": "+27 12 664 1234",
        "address_line1": "15 Lenchen Avenue",
        "address_line2": "Centurion Gate",
        "city": "Centurion",
        "province": "Gauteng",
        "postal_code": "0157",
        "country": "ZA",
        "latitude": -25.8603,
        "longitude": 28.1894,
    },
]


def seed_gyms(session: Session) -> list[Gym]:
    """Seed sample gyms idempotently.

    Checks for existing gyms by slug before creating new ones.
    This ensures the seed can be run multiple times safely.

    Args:
        session: SQLModel database session

    Returns:
        List of all seeded/existing Gym objects
    """
    gyms: list[Gym] = []

    for gym_data in SEED_GYMS:
        # Check if gym already exists by unique slug
        existing = session.exec(select(Gym).where(Gym.slug == gym_data["slug"])).first()

        if existing:
            gyms.append(existing)
            continue

        # Create new gym
        gym = Gym(**gym_data)
        session.add(gym)
        gyms.append(gym)

    session.commit()

    # Refresh to get generated IDs
    for gym in gyms:
        session.refresh(gym)

    return gyms
