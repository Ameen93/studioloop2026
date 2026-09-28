"""Seed data for Consumer entities.

Creates realistic South African consumer profiles for testing.
Names represent SA's diverse population (Zulu, Afrikaans, Indian, English, etc.).
Phone numbers use correct SA mobile format (+27 XX XXX XXXX).
"""

from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models import Consumer
from app.models.consumer import UserRole

# Diverse South African names representing different cultural backgrounds
SEED_CONSUMERS: list[dict[str, Any]] = [
    # Test account for development (always first)
    {
        "email": "test@studioloop.com",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+27 82 000 0001",
        "hashed_password": get_password_hash("testpassword123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
        "role": UserRole.CONSUMER,
    },
    # Zulu names
    {
        "email": "thandi.nkosi@example.com",
        "first_name": "Thandi",
        "last_name": "Nkosi",
        "phone": "+27 83 456 7890",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
        "role": UserRole.CONSUMER,
    },
    {
        "email": "sipho.dlamini@example.com",
        "first_name": "Sipho",
        "last_name": "Dlamini",
        "phone": "+27 72 234 5678",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": False,
        "accepts_marketing": False,
        "role": UserRole.CONSUMER,
    },
    {
        "email": "nomvula.zulu@example.com",
        "first_name": "Nomvula",
        "last_name": "Zulu",
        "phone": "+27 84 876 5432",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
        "role": UserRole.CONSUMER,
    },
    # Afrikaans names
    {
        "email": "pieter.vandermerwe@example.com",
        "first_name": "Pieter",
        "last_name": "van der Merwe",
        "phone": "+27 82 345 6789",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": False,
        "role": UserRole.CONSUMER,
    },
    {
        "email": "annemarie.botha@example.com",
        "first_name": "Annemarie",
        "last_name": "Botha",
        "phone": "+27 73 567 8901",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": False,
        "is_phone_verified": False,
        "accepts_marketing": True,
        "role": UserRole.CONSUMER,
    },
    {
        "email": "johan.pretorius@example.com",
        "first_name": "Johan",
        "last_name": "Pretorius",
        "phone": "+27 81 234 5678",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
        "role": UserRole.CONSUMER,
    },
    # Indian names
    {
        "email": "priya.naidoo@example.com",
        "first_name": "Priya",
        "last_name": "Naidoo",
        "phone": "+27 82 789 0123",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
        "role": UserRole.CONSUMER,
    },
    {
        "email": "raj.pillay@example.com",
        "first_name": "Raj",
        "last_name": "Pillay",
        "phone": "+27 74 321 0987",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": False,
        "accepts_marketing": False,
        "role": UserRole.CONSUMER,
    },
    {
        "email": "fatima.patel@example.com",
        "first_name": "Fatima",
        "last_name": "Patel",
        "phone": "+27 83 654 3210",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
        "role": UserRole.CONSUMER,
    },
    # English names
    {
        "email": "john.smith@example.com",
        "first_name": "John",
        "last_name": "Smith",
        "phone": "+27 82 111 2222",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": False,
        "role": UserRole.CONSUMER,
    },
    {
        "email": "sarah.jones@example.com",
        "first_name": "Sarah",
        "last_name": "Jones",
        "phone": "+27 71 333 4444",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
        "role": UserRole.CONSUMER,
    },
    # Sotho names
    {
        "email": "lerato.molefe@example.com",
        "first_name": "Lerato",
        "last_name": "Molefe",
        "phone": "+27 82 555 6666",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
        "role": UserRole.CONSUMER,
    },
    {
        "email": "mpho.mokoena@example.com",
        "first_name": "Mpho",
        "last_name": "Mokoena",
        "phone": "+27 84 777 8888",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": False,
        "is_phone_verified": False,
        "accepts_marketing": False,
        "role": UserRole.CONSUMER,
    },
    # Xhosa names
    {
        "email": "andile.mthembu@example.com",
        "first_name": "Andile",
        "last_name": "Mthembu",
        "phone": "+27 73 999 0000",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
        "role": UserRole.CONSUMER,
    },
    {
        "email": "noluthando.ngcobo@example.com",
        "first_name": "Noluthando",
        "last_name": "Ngcobo",
        "phone": "+27 82 123 4567",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": False,
        "accepts_marketing": True,
        "role": UserRole.CONSUMER,
    },
]


def seed_consumers(session: Session) -> list[Consumer]:
    """Seed sample consumers idempotently.

    Checks for existing consumers by email before creating new ones.
    Includes a test account (test@studioloop.com) for development.

    Args:
        session: SQLModel database session

    Returns:
        List of all seeded/existing Consumer objects
    """
    consumers: list[Consumer] = []

    for consumer_data in SEED_CONSUMERS:
        # Check if consumer already exists by unique email
        existing = session.exec(
            select(Consumer).where(Consumer.email == consumer_data["email"])
        ).first()

        if existing:
            consumers.append(existing)
            continue

        # Create new consumer
        consumer = Consumer(**consumer_data)
        session.add(consumer)
        consumers.append(consumer)

    session.commit()

    return consumers
