"""Seed data for Staff entities.

Creates realistic South African staff members for each gym.
Each gym gets an owner, managers, front desk staff, and instructors.
"""

from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models import Gym, Staff
from app.models.staff import StaffRole

# Staff templates per gym - keyed by gym slug
# Each staff member gets realistic SA names and roles
SEED_STAFF: dict[str, list[dict[str, Any]]] = {
    "fitzone-sandton": [
        {
            "email": "owner@fitzone-sandton.co.za",
            "first_name": "Kabelo",
            "last_name": "Moagi",
            "role": StaffRole.OWNER,
            "phone": "+27 82 100 0001",
            "is_email_verified": True,
        },
        {
            "email": "manager@fitzone-sandton.co.za",
            "first_name": "Lindiwe",
            "last_name": "Khumalo",
            "role": StaffRole.MANAGER,
            "phone": "+27 82 100 0002",
            "is_email_verified": True,
        },
        {
            "email": "frontdesk@fitzone-sandton.co.za",
            "first_name": "Tumelo",
            "last_name": "Mahlangu",
            "role": StaffRole.FRONT_DESK,
            "phone": "+27 82 100 0003",
            "is_email_verified": True,
        },
        {
            "email": "yoga.instructor@fitzone-sandton.co.za",
            "first_name": "Naledi",
            "last_name": "Tshabalala",
            "role": StaffRole.INSTRUCTOR,
            "phone": "+27 82 100 0004",
            "is_email_verified": True,
            "working_hours": {
                "monday": {"start": "06:00", "end": "12:00", "off": False},
                "tuesday": {"start": "06:00", "end": "12:00", "off": False},
                "wednesday": {"start": "06:00", "end": "12:00", "off": False},
                "thursday": {"start": "06:00", "end": "12:00", "off": False},
                "friday": {"start": "06:00", "end": "12:00", "off": False},
                "saturday": {"start": "08:00", "end": "11:00", "off": False},
                "sunday": {"start": None, "end": None, "off": True},
            },
        },
        {
            "email": "spin.instructor@fitzone-sandton.co.za",
            "first_name": "Bongani",
            "last_name": "Ndlovu",
            "role": StaffRole.INSTRUCTOR,
            "phone": "+27 82 100 0005",
            "is_email_verified": True,
            "working_hours": {
                "monday": {"start": "16:00", "end": "21:00", "off": False},
                "tuesday": {"start": "16:00", "end": "21:00", "off": False},
                "wednesday": {"start": "16:00", "end": "21:00", "off": False},
                "thursday": {"start": "16:00", "end": "21:00", "off": False},
                "friday": {"start": "16:00", "end": "20:00", "off": False},
                "saturday": {"start": "09:00", "end": "13:00", "off": False},
                "sunday": {"start": None, "end": None, "off": True},
            },
        },
    ],
    "oxygen-cape-town": [
        {
            "email": "owner@oxygenfitness.co.za",
            "first_name": "Chantal",
            "last_name": "du Plessis",
            "role": StaffRole.OWNER,
            "phone": "+27 82 200 0001",
            "is_email_verified": True,
        },
        {
            "email": "manager@oxygenfitness.co.za",
            "first_name": "Mandla",
            "last_name": "Sithole",
            "role": StaffRole.MANAGER,
            "phone": "+27 82 200 0002",
            "is_email_verified": True,
        },
        {
            "email": "frontdesk@oxygenfitness.co.za",
            "first_name": "Zandile",
            "last_name": "Mkhize",
            "role": StaffRole.FRONT_DESK,
            "phone": "+27 82 200 0003",
            "is_email_verified": True,
        },
        {
            "email": "yoga@oxygenfitness.co.za",
            "first_name": "Emma",
            "last_name": "Williams",
            "role": StaffRole.INSTRUCTOR,
            "phone": "+27 82 200 0004",
            "is_email_verified": True,
        },
    ],
    "pure-energy-pretoria": [
        {
            "email": "owner@pureenergy.co.za",
            "first_name": "Hennie",
            "last_name": "Venter",
            "role": StaffRole.OWNER,
            "phone": "+27 82 300 0001",
            "is_email_verified": True,
        },
        {
            "email": "manager@pureenergy.co.za",
            "first_name": "Precious",
            "last_name": "Dube",
            "role": StaffRole.MANAGER,
            "phone": "+27 82 300 0002",
            "is_email_verified": True,
        },
        {
            "email": "hiit@pureenergy.co.za",
            "first_name": "Siyabonga",
            "last_name": "Zwane",
            "role": StaffRole.INSTRUCTOR,
            "phone": "+27 82 300 0003",
            "is_email_verified": True,
        },
    ],
    "sweat-box-durban": [
        {
            "email": "owner@thesweatbox.co.za",
            "first_name": "Vikash",
            "last_name": "Govender",
            "role": StaffRole.OWNER,
            "phone": "+27 82 400 0001",
            "is_email_verified": True,
        },
        {
            "email": "manager@thesweatbox.co.za",
            "first_name": "Nokukhanya",
            "last_name": "Cele",
            "role": StaffRole.MANAGER,
            "phone": "+27 82 400 0002",
            "is_email_verified": True,
        },
        {
            "email": "frontdesk@thesweatbox.co.za",
            "first_name": "Ayanda",
            "last_name": "Mnguni",
            "role": StaffRole.FRONT_DESK,
            "phone": "+27 82 400 0003",
            "is_email_verified": True,
        },
    ],
    "crossfit-centurion": [
        {
            "email": "owner@crossfitcenturion.co.za",
            "first_name": "Jacques",
            "last_name": "Steyn",
            "role": StaffRole.OWNER,
            "phone": "+27 82 500 0001",
            "is_email_verified": True,
        },
        {
            "email": "coach@crossfitcenturion.co.za",
            "first_name": "Ruan",
            "last_name": "de Villiers",
            "role": StaffRole.INSTRUCTOR,
            "phone": "+27 82 500 0002",
            "is_email_verified": True,
        },
    ],
}

_DEFAULT_PASSWORD = get_password_hash("staffpass123")


def seed_staff(session: Session, gyms: list[Gym]) -> int:
    """Seed staff members for each gym idempotently.

    Checks for existing staff by email before creating.
    All staff get password 'staffpass123' for local testing.

    Args:
        session: SQLModel database session
        gyms: List of Gym objects to create staff for

    Returns:
        Number of staff members created/found
    """
    count = 0
    gym_by_slug = {g.slug: g for g in gyms}

    for slug, staff_list in SEED_STAFF.items():
        gym = gym_by_slug.get(slug)
        if not gym:
            continue

        for staff_data in staff_list:
            existing = session.exec(
                select(Staff).where(Staff.email == staff_data["email"])
            ).first()
            if existing:
                count += 1
                continue

            staff = Staff(
                gym_id=gym.id,
                email=staff_data["email"],
                first_name=staff_data["first_name"],
                last_name=staff_data["last_name"],
                role=staff_data["role"],
                phone=staff_data.get("phone"),
                is_email_verified=staff_data.get("is_email_verified", True),
                hashed_password=_DEFAULT_PASSWORD,
                working_hours=staff_data.get("working_hours", {}),
            )
            session.add(staff)
            count += 1

    session.commit()
    return count
