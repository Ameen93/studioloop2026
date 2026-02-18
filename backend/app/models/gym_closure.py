"""Gym closure dates (Story 2.4)."""

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.gym import Gym


class GymClosureBase(SQLModel):
    """Base properties shared by gym closure schemas."""

    closure_date: date = Field(description="Date when gym is closed")
    reason: str | None = Field(
        default=None,
        max_length=255,
        description="Optional reason shown to members (e.g. Christmas Day)",
    )


class GymClosure(BaseModel, GymClosureBase, table=True):
    """Gym-specific closure dates used for scheduling validation and public display."""

    __tablename__ = "gym_closures"
    __table_args__ = (
        UniqueConstraint("gym_id", "closure_date", name="uq_gym_closures_gym_date"),
    )

    gym_id: UUID = Field(foreign_key="gyms.id", nullable=False, index=True)

    gym: "Gym" = Relationship(back_populates="closures")


class GymClosureCreate(GymClosureBase):
    """Request payload to create a closure date."""


class GymClosurePublic(GymClosureBase):
    """Public closure details."""

    id: UUID
    gym_id: UUID
