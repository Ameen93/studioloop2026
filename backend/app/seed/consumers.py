"""Seed data for Consumer entities.

Creates realistic South African consumer profiles for testing.
Names represent SA's diverse population (Zulu, Afrikaans, Indian, English, etc.).
Phone numbers use correct SA mobile format (+27 XX XXX XXXX).
"""

from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models import Consumer

# Diverse South African names representing different cultural backgrounds
SEED_CONSUMERS: list[dict[str, Any]] = [
    # Test account for development (always first)
    {
        "email": "test@studioloop.com",
        "full_name": "Test User",
        "phone": "+27 82 000 0001",
        "hashed_password": get_password_hash("testpassword123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
    },
    # Zulu names
    {
        "email": "thandi.nkosi@gmail.com",
        "full_name": "Thandi Nkosi",
        "phone": "+27 83 456 7890",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
    },
    {
        "email": "sipho.dlamini@outlook.com",
        "full_name": "Sipho Dlamini",
        "phone": "+27 72 234 5678",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": False,
        "accepts_marketing": False,
    },
    {
        "email": "nomvula.zulu@yahoo.com",
        "full_name": "Nomvula Zulu",
        "phone": "+27 84 876 5432",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
    },
    # Afrikaans names
    {
        "email": "pieter.vandermerwe@gmail.com",
        "full_name": "Pieter van der Merwe",
        "phone": "+27 82 345 6789",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": False,
    },
    {
        "email": "annemarie.botha@outlook.com",
        "full_name": "Annemarie Botha",
        "phone": "+27 73 567 8901",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": False,
        "is_phone_verified": False,
        "accepts_marketing": True,
    },
    {
        "email": "johan.pretorius@gmail.com",
        "full_name": "Johan Pretorius",
        "phone": "+27 81 234 5678",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
    },
    # Indian names
    {
        "email": "priya.naidoo@gmail.com",
        "full_name": "Priya Naidoo",
        "phone": "+27 82 789 0123",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
    },
    {
        "email": "raj.pillay@outlook.com",
        "full_name": "Raj Pillay",
        "phone": "+27 74 321 0987",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": False,
        "accepts_marketing": False,
    },
    {
        "email": "fatima.patel@yahoo.com",
        "full_name": "Fatima Patel",
        "phone": "+27 83 654 3210",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
    },
    # English names
    {
        "email": "john.smith@gmail.com",
        "full_name": "John Smith",
        "phone": "+27 82 111 2222",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": False,
    },
    {
        "email": "sarah.jones@outlook.com",
        "full_name": "Sarah Jones",
        "phone": "+27 71 333 4444",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
    },
    # Sotho names
    {
        "email": "lerato.molefe@gmail.com",
        "full_name": "Lerato Molefe",
        "phone": "+27 82 555 6666",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
    },
    {
        "email": "mpho.mokoena@yahoo.com",
        "full_name": "Mpho Mokoena",
        "phone": "+27 84 777 8888",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": False,
        "is_phone_verified": False,
        "accepts_marketing": False,
    },
    # Xhosa names
    {
        "email": "andile.mthembu@gmail.com",
        "full_name": "Andile Mthembu",
        "phone": "+27 73 999 0000",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": True,
        "accepts_marketing": True,
    },
    {
        "email": "noluthando.ngcobo@outlook.com",
        "full_name": "Noluthando Ngcobo",
        "phone": "+27 82 123 4567",
        "hashed_password": get_password_hash("password123"),
        "is_email_verified": True,
        "is_phone_verified": False,
        "accepts_marketing": True,
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

    # Refresh to get generated IDs
    for consumer in consumers:
        session.refresh(consumer)

    return consumers
