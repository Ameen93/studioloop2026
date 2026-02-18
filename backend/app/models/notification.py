from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID

from sqlmodel import JSON, Column, Field

from app.models.base import BaseModel


class NotificationChannel(StrEnum):
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    WHATSAPP = "whatsapp"


class NotificationType(StrEnum):
    BOOKING_CONFIRMATION = "booking_confirmation"
    CLASS_REMINDER = "class_reminder"
    WAITLIST_SPOT_AVAILABLE = "waitlist_spot_available"
    PAYMENT_REMINDER = "payment_reminder"
    PAYMENT_FAILURE = "payment_failure"
    GYM_MESSAGE = "gym_message"
    CLASS_CANCELLED = "class_cancelled"
    EMERGENCY_CLOSURE = "emergency_closure"


class NotificationStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class Notification(BaseModel, table=True):
    __tablename__ = "notifications"

    consumer_id: UUID = Field(foreign_key="consumers.id", nullable=False, index=True)
    gym_id: UUID | None = Field(default=None, foreign_key="gyms.id", index=True)
    notification_type: NotificationType = Field(max_length=40, index=True)
    channel: NotificationChannel = Field(max_length=20, index=True)
    title: str = Field(max_length=255)
    body: str = Field(max_length=2000)
    data: dict[str, str | int | bool | None] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    status: NotificationStatus = Field(
        default=NotificationStatus.PENDING, max_length=20, index=True
    )
    is_read: bool = Field(default=False, index=True)
    read_at: datetime | None = Field(default=None)
    sent_at: datetime | None = Field(default=None)
    delivered_at: datetime | None = Field(default=None)
    failed_at: datetime | None = Field(default=None)
    failure_reason: str | None = Field(default=None, max_length=500)
    template_id: str | None = Field(default=None, max_length=100)
    related_entity_id: UUID | None = Field(default=None, index=True)
    scheduled_for: datetime | None = Field(default=None, index=True)

    def mark_sent(self) -> None:
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.now(timezone.utc)

    def mark_delivered(self) -> None:
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = datetime.now(timezone.utc)

    def mark_failed(self, reason: str) -> None:
        self.status = NotificationStatus.FAILED
        self.failed_at = datetime.now(timezone.utc)
        self.failure_reason = reason[:500]

    def mark_read(self) -> None:
        self.is_read = True
        self.read_at = datetime.now(timezone.utc)


class NotificationTemplate(BaseModel, table=True):
    __tablename__ = "notification_templates"

    name: str = Field(max_length=100, unique=True, index=True)
    notification_type: NotificationType = Field(max_length=40)
    channel: NotificationChannel = Field(max_length=20)
    title_template: str = Field(max_length=500)
    body_template: str = Field(max_length=4000)
    is_active: bool = Field(default=True)


class NotificationPreference(BaseModel, table=True):
    __tablename__ = "notification_preferences"

    consumer_id: UUID = Field(
        foreign_key="consumers.id", nullable=False, unique=True, index=True
    )
    booking_push: bool = Field(default=True)
    booking_email: bool = Field(default=True)
    reminder_push: bool = Field(default=True)
    reminder_email: bool = Field(default=False)
    reminder_timing_hours: str = Field(default="2,24", max_length=50)
    waitlist_push: bool = Field(default=True)
    waitlist_email: bool = Field(default=True)
    payment_push: bool = Field(default=True)
    payment_email: bool = Field(default=True)
    gym_message_push: bool = Field(default=True)
    gym_message_email: bool = Field(default=True)
    whatsapp_enabled: bool = Field(default=True)


class GymMessage(BaseModel, table=True):
    __tablename__ = "gym_messages"

    gym_id: UUID = Field(foreign_key="gyms.id", nullable=False, index=True)
    sender_staff_id: UUID = Field(foreign_key="staff.id", nullable=False, index=True)
    subject: str = Field(max_length=255)
    body: str = Field(max_length=4000)
    recipient_filter: str = Field(
        default="all", max_length=50
    )  # all, plan:<id>, individual
    recipient_ids: list[str] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )
    channels: list[str] = Field(
        default_factory=lambda: ["in_app"],
        sa_column=Column("delivery_channels", JSON, nullable=False),
    )
    scheduled_for: datetime | None = Field(default=None)
    sent_at: datetime | None = Field(default=None)
    total_recipients: int = Field(default=0, ge=0)
    delivered_count: int = Field(default=0, ge=0)
    failed_count: int = Field(default=0, ge=0)
