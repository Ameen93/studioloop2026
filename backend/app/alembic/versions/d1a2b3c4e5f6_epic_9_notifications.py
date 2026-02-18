"""epic 9 notifications and communication

Revision ID: d1a2b3c4e5f6
Revises: c9e2b1f0a8d1
Create Date: 2026-02-18 14:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "d1a2b3c4e5f6"
down_revision = "c9e2b1f0a8d1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("consumer_id", sa.Uuid(), nullable=False),
        sa.Column("gym_id", sa.Uuid(), nullable=True),
        sa.Column("notification_type", sa.String(length=40), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.String(length=2000), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, default=False),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.Column("failed_at", sa.DateTime(), nullable=True),
        sa.Column("failure_reason", sa.String(length=500), nullable=True),
        sa.Column("template_id", sa.String(length=100), nullable=True),
        sa.Column("related_entity_id", sa.Uuid(), nullable=True),
        sa.Column("scheduled_for", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["consumer_id"], ["consumers.id"]),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_consumer_id", "notifications", ["consumer_id"])
    op.create_index("ix_notifications_gym_id", "notifications", ["gym_id"])
    op.create_index("ix_notifications_notification_type", "notifications", ["notification_type"])
    op.create_index("ix_notifications_channel", "notifications", ["channel"])
    op.create_index("ix_notifications_status", "notifications", ["status"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])
    op.create_index("ix_notifications_scheduled_for", "notifications", ["scheduled_for"])
    op.create_index("ix_notifications_related_entity_id", "notifications", ["related_entity_id"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])

    op.create_table(
        "notification_templates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("notification_type", sa.String(length=40), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("title_template", sa.String(length=500), nullable=False),
        sa.Column("body_template", sa.String(length=4000), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_notification_templates_name", "notification_templates", ["name"])

    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("consumer_id", sa.Uuid(), nullable=False),
        sa.Column("booking_push", sa.Boolean(), nullable=False, default=True),
        sa.Column("booking_email", sa.Boolean(), nullable=False, default=True),
        sa.Column("reminder_push", sa.Boolean(), nullable=False, default=True),
        sa.Column("reminder_email", sa.Boolean(), nullable=False, default=False),
        sa.Column("reminder_timing_hours", sa.String(length=50), nullable=False),
        sa.Column("waitlist_push", sa.Boolean(), nullable=False, default=True),
        sa.Column("waitlist_email", sa.Boolean(), nullable=False, default=True),
        sa.Column("payment_push", sa.Boolean(), nullable=False, default=True),
        sa.Column("payment_email", sa.Boolean(), nullable=False, default=True),
        sa.Column("gym_message_push", sa.Boolean(), nullable=False, default=True),
        sa.Column("gym_message_email", sa.Boolean(), nullable=False, default=True),
        sa.Column("whatsapp_enabled", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["consumer_id"], ["consumers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("consumer_id"),
    )
    op.create_index("ix_notification_preferences_consumer_id", "notification_preferences", ["consumer_id"])

    op.create_table(
        "gym_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("gym_id", sa.Uuid(), nullable=False),
        sa.Column("sender_staff_id", sa.Uuid(), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("body", sa.String(length=4000), nullable=False),
        sa.Column("recipient_filter", sa.String(length=50), nullable=False),
        sa.Column("recipient_ids", sa.JSON(), nullable=False),
        sa.Column("delivery_channels", sa.JSON(), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("total_recipients", sa.Integer(), nullable=False, default=0),
        sa.Column("delivered_count", sa.Integer(), nullable=False, default=0),
        sa.Column("failed_count", sa.Integer(), nullable=False, default=0),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.id"]),
        sa.ForeignKeyConstraint(["sender_staff_id"], ["staff.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gym_messages_gym_id", "gym_messages", ["gym_id"])
    op.create_index("ix_gym_messages_sender_staff_id", "gym_messages", ["sender_staff_id"])


def downgrade() -> None:
    op.drop_table("gym_messages")
    op.drop_table("notification_preferences")
    op.drop_table("notification_templates")
    op.drop_table("notifications")
