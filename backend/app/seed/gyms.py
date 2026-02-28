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
        "description": "Sandton's premier fitness destination, featuring a 500sqm open-plan gym floor, dedicated group training studios, and a rooftop recovery lounge. Home to 12 certified trainers and over 400 active members.",
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
        "description": "Cape Town's most-loved seaside studio, known for sunrise yoga with ocean views and high-energy evening HIIT. Two floors, four studios, and a smoothie bar. Proudly community-driven since 2019.",
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
        "description": "Brooklyn's go-to fitness hub with group classes, personal training, and a welcoming vibe for all fitness levels. Specialising in strength training and functional fitness for busy professionals.",
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
        "description": "Durban's original boutique HIIT studio on Florida Road. Small classes, big energy, real results. Known for our 30-minute lunchtime express sessions and Saturday morning community workouts.",
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
        "description": "Centurion's first CrossFit affiliate, built by athletes for athletes. Structured programming, Olympic lifting coaching, and a tight-knit community of 80+ members who push each other daily.",
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

    return gyms
