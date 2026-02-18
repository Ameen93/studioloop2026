from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import GymScopedSoftDeleteModel


class ClassSessionStatus(StrEnum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"


class ClassSessionBase(SQLModel):
    space_id: UUID = Field(foreign_key="spaces.id", nullable=False, index=True)
    title: str = Field(min_length=1, max_length=255)
    start_time: datetime
    end_time: datetime
    status: ClassSessionStatus = Field(default=ClassSessionStatus.SCHEDULED, max_length=20)


class ClassSession(GymScopedSoftDeleteModel, ClassSessionBase, table=True):
    __tablename__ = "class_sessions"


class ClassSessionCreate(SQLModel):
    space_id: UUID
    title: str = Field(min_length=1, max_length=255)
    start_time: datetime
    end_time: datetime


class ClassSessionPublic(SQLModel):
    id: UUID
    gym_id: UUID
    space_id: UUID
    title: str
    start_time: datetime
    end_time: datetime
    status: ClassSessionStatus
