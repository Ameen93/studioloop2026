from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import GymScopedSoftDeleteModel
from app.models.class_template import ClassType


class ClassSessionStatus(StrEnum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"


class ApprovalStatus(StrEnum):
    AUTO_APPROVED = "auto_approved"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class ClassSessionBase(SQLModel):
    space_id: UUID = Field(foreign_key="spaces.id", nullable=False, index=True)
    instructor_staff_id: UUID | None = Field(
        default=None, foreign_key="staff.id", index=True
    )
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    class_type: ClassType | None = Field(default=None, max_length=20)
    start_time: datetime
    end_time: datetime
    status: ClassSessionStatus = Field(
        default=ClassSessionStatus.SCHEDULED, max_length=20
    )
    capacity: int = Field(default=0, ge=0)
    spots_booked: int = Field(default=0, ge=0)
    waitlist_enabled: bool = Field(default=True)
    waitlist_capacity: int = Field(default=0, ge=0)
    price_cents: int = Field(default=0, ge=0)
    class_template_id: UUID | None = Field(
        default=None, foreign_key="class_templates.id", index=True
    )
    recurrence_group_id: UUID | None = Field(default=None, index=True)
    approval_status: ApprovalStatus = Field(
        default=ApprovalStatus.AUTO_APPROVED, max_length=20
    )
    created_by_staff_id: UUID | None = Field(default=None, foreign_key="staff.id")
    cancellation_reason: str | None = Field(default=None, max_length=500)
    cancelled_by_staff_id: UUID | None = Field(default=None, foreign_key="staff.id")
    marketplace_visible: bool = Field(default=True)


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
    instructor_staff_id: UUID | None
    title: str
    description: str | None
    class_type: ClassType | None
    start_time: datetime
    end_time: datetime
    status: ClassSessionStatus
    capacity: int
    spots_booked: int
    waitlist_enabled: bool
    waitlist_capacity: int
    price_cents: int
    class_template_id: UUID | None
    recurrence_group_id: UUID | None
    approval_status: ApprovalStatus
    created_by_staff_id: UUID | None
    cancellation_reason: str | None
    cancelled_by_staff_id: UUID | None
    marketplace_visible: bool
