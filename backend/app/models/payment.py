from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID

from sqlmodel import JSON, Column, Field

from app.models.base import BaseModel, GymScopedModel


class PaymentType(StrEnum):
    MEMBERSHIP = "membership"
    CLASS_BOOKING = "class_booking"
    MARKETPLACE_SUBSCRIPTION = "marketplace_subscription"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    FAILED_PERMANENT = "failed_permanent"
    REFUNDED = "refunded"


class PaymentProviderName(StrEnum):
    OZOW = "ozow"
    PAYFAST = "payfast"


class Payment(GymScopedModel, table=True):
    __tablename__ = "payments"

    consumer_id: UUID = Field(foreign_key="consumers.id", nullable=False, index=True)
    amount_cents: int = Field(ge=0, nullable=False)
    currency: str = Field(default="ZAR", max_length=3)
    payment_type: PaymentType = Field(default=PaymentType.MEMBERSHIP, max_length=40)
    status: PaymentStatus = Field(
        default=PaymentStatus.PENDING, max_length=24, index=True
    )
    provider: PaymentProviderName = Field(
        default=PaymentProviderName.OZOW, max_length=20
    )
    provider_reference: str | None = Field(default=None, max_length=255, index=True)
    description: str = Field(max_length=255)
    return_url: str | None = Field(default=None, max_length=500)
    cancel_url: str | None = Field(default=None, max_length=500)
    webhook_url: str | None = Field(default=None, max_length=500)
    related_entity_id: UUID | None = Field(default=None, index=True)
    failed_at: datetime | None = Field(default=None)
    failure_reason: str | None = Field(default=None, max_length=500)
    retry_count: int = Field(default=0, ge=0)
    max_retry_attempts: int = Field(default=3, ge=0)
    next_retry_at: datetime | None = Field(default=None, index=True)
    completed_at: datetime | None = Field(default=None)
    refunded_at: datetime | None = Field(default=None)
    extra_data: dict[str, str | int | bool | None] = Field(
        default_factory=dict, sa_column=Column("metadata", JSON, nullable=False)
    )

    def mark_completed(self, provider_reference: str | None = None) -> None:
        self.status = PaymentStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        if provider_reference:
            self.provider_reference = provider_reference
        self.failure_reason = None
        self.failed_at = None
        self.next_retry_at = None

    def mark_failed(self, reason: str, next_retry_at: datetime | None = None) -> None:
        self.status = PaymentStatus.FAILED
        self.failed_at = datetime.now(timezone.utc)
        self.failure_reason = reason[:500]
        self.next_retry_at = next_retry_at

    def mark_refunded(self, provider_reference: str | None = None) -> None:
        self.status = PaymentStatus.REFUNDED
        self.refunded_at = datetime.now(timezone.utc)
        if provider_reference:
            self.provider_reference = provider_reference


class PaymentWebhookEvent(BaseModel, table=True):
    __tablename__ = "payment_webhook_events"

    provider: PaymentProviderName = Field(max_length=20)
    event_id: str = Field(max_length=255, index=True, unique=True)
    payment_id: UUID | None = Field(default=None, foreign_key="payments.id", index=True)
    event_type: str = Field(max_length=64)
    signature_valid: bool = Field(default=False)
    payload: dict[str, str | int | bool | None] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )


class PaymentReceipt(BaseModel, table=True):
    __tablename__ = "payment_receipts"

    payment_id: UUID = Field(
        foreign_key="payments.id", nullable=False, index=True, unique=True
    )
    consumer_id: UUID = Field(foreign_key="consumers.id", nullable=False, index=True)
    receipt_number: str = Field(max_length=64, index=True, unique=True)
    vat_rate_percent: float = Field(default=15.0, ge=0)
    vat_amount_cents: int = Field(default=0, ge=0)
    subtotal_cents: int = Field(default=0, ge=0)
    total_cents: int = Field(default=0, ge=0)
    rendered_text: str = Field(max_length=4000)
    emailed_at: datetime | None = Field(default=None)
