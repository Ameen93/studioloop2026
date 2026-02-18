"""epic 8 payments and billing

Revision ID: c9e2b1f0a8d1
Revises: b7e7a1d9c245
Create Date: 2026-02-18 12:45:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "c9e2b1f0a8d1"
down_revision = "b7e7a1d9c245"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("gym_id", sa.Uuid(), nullable=False),
        sa.Column("consumer_id", sa.Uuid(), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("payment_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("provider_reference", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("return_url", sa.String(length=500), nullable=True),
        sa.Column("cancel_url", sa.String(length=500), nullable=True),
        sa.Column("webhook_url", sa.String(length=500), nullable=True),
        sa.Column("related_entity_id", sa.Uuid(), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.String(length=500), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("max_retry_attempts", sa.Integer(), nullable=False),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["consumer_id"], ["consumers.id"]),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payments_consumer_id"), "payments", ["consumer_id"], unique=False)
    op.create_index(op.f("ix_payments_created_at"), "payments", ["created_at"], unique=False)
    op.create_index(op.f("ix_payments_gym_id"), "payments", ["gym_id"], unique=False)
    op.create_index(op.f("ix_payments_id"), "payments", ["id"], unique=False)
    op.create_index(op.f("ix_payments_next_retry_at"), "payments", ["next_retry_at"], unique=False)
    op.create_index(op.f("ix_payments_provider_reference"), "payments", ["provider_reference"], unique=False)
    op.create_index(op.f("ix_payments_related_entity_id"), "payments", ["related_entity_id"], unique=False)
    op.create_index(op.f("ix_payments_status"), "payments", ["status"], unique=False)

    op.create_table(
        "payment_webhook_events",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("event_id", sa.String(length=255), nullable=False),
        sa.Column("payment_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("signature_valid", sa.Boolean(), nullable=False),
        sa.Column("payload", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )
    op.create_index(op.f("ix_payment_webhook_events_created_at"), "payment_webhook_events", ["created_at"], unique=False)
    op.create_index(op.f("ix_payment_webhook_events_event_id"), "payment_webhook_events", ["event_id"], unique=False)
    op.create_index(op.f("ix_payment_webhook_events_id"), "payment_webhook_events", ["id"], unique=False)
    op.create_index(op.f("ix_payment_webhook_events_payment_id"), "payment_webhook_events", ["payment_id"], unique=False)

    op.create_table(
        "payment_receipts",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("payment_id", sa.Uuid(), nullable=False),
        sa.Column("consumer_id", sa.Uuid(), nullable=False),
        sa.Column("receipt_number", sa.String(length=64), nullable=False),
        sa.Column("vat_rate_percent", sa.Float(), nullable=False),
        sa.Column("vat_amount_cents", sa.Integer(), nullable=False),
        sa.Column("subtotal_cents", sa.Integer(), nullable=False),
        sa.Column("total_cents", sa.Integer(), nullable=False),
        sa.Column("rendered_text", sa.String(length=4000), nullable=False),
        sa.Column("emailed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["consumer_id"], ["consumers.id"]),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_id"),
        sa.UniqueConstraint("receipt_number"),
    )
    op.create_index(op.f("ix_payment_receipts_consumer_id"), "payment_receipts", ["consumer_id"], unique=False)
    op.create_index(op.f("ix_payment_receipts_created_at"), "payment_receipts", ["created_at"], unique=False)
    op.create_index(op.f("ix_payment_receipts_id"), "payment_receipts", ["id"], unique=False)
    op.create_index(op.f("ix_payment_receipts_payment_id"), "payment_receipts", ["payment_id"], unique=False)
    op.create_index(op.f("ix_payment_receipts_receipt_number"), "payment_receipts", ["receipt_number"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_payment_receipts_receipt_number"), table_name="payment_receipts")
    op.drop_index(op.f("ix_payment_receipts_payment_id"), table_name="payment_receipts")
    op.drop_index(op.f("ix_payment_receipts_id"), table_name="payment_receipts")
    op.drop_index(op.f("ix_payment_receipts_created_at"), table_name="payment_receipts")
    op.drop_index(op.f("ix_payment_receipts_consumer_id"), table_name="payment_receipts")
    op.drop_table("payment_receipts")

    op.drop_index(op.f("ix_payment_webhook_events_payment_id"), table_name="payment_webhook_events")
    op.drop_index(op.f("ix_payment_webhook_events_id"), table_name="payment_webhook_events")
    op.drop_index(op.f("ix_payment_webhook_events_event_id"), table_name="payment_webhook_events")
    op.drop_index(op.f("ix_payment_webhook_events_created_at"), table_name="payment_webhook_events")
    op.drop_table("payment_webhook_events")

    op.drop_index(op.f("ix_payments_status"), table_name="payments")
    op.drop_index(op.f("ix_payments_related_entity_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_provider_reference"), table_name="payments")
    op.drop_index(op.f("ix_payments_next_retry_at"), table_name="payments")
    op.drop_index(op.f("ix_payments_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_gym_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_created_at"), table_name="payments")
    op.drop_index(op.f("ix_payments_consumer_id"), table_name="payments")
    op.drop_table("payments")
