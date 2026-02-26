"""add marketplace subscription and referral tables

Revision ID: b7e7a1d9c245
Revises: f2d9a30f7b11
Create Date: 2026-02-18 12:10:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b7e7a1d9c245"
down_revision = "f2d9a30f7b11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "marketplace_subscriptions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumer_id", sa.Uuid(), nullable=False),
        sa.Column("plan_tier", sa.String(length=20), nullable=False),
        sa.Column("classes_total", sa.Integer(), nullable=False),
        sa.Column("classes_remaining", sa.Integer(), nullable=False),
        sa.Column("reset_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("paused_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("downgrade_to_tier", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(["consumer_id"], ["consumers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_marketplace_subscriptions_consumer_id"), "marketplace_subscriptions", ["consumer_id"], unique=False)
    op.create_index(op.f("ix_marketplace_subscriptions_created_at"), "marketplace_subscriptions", ["created_at"], unique=False)

    op.create_table(
        "referral_invites",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("referrer_consumer_id", sa.Uuid(), nullable=False),
        sa.Column("referral_code", sa.String(length=64), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("class_session_id", sa.Uuid(), nullable=True),
        sa.Column("referred_email_hash", sa.String(length=128), nullable=True),
        sa.Column("signed_up_consumer_id", sa.Uuid(), nullable=True),
        sa.Column("signed_up_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["class_session_id"], ["class_sessions.id"]),
        sa.ForeignKeyConstraint(["referrer_consumer_id"], ["consumers.id"]),
        sa.ForeignKeyConstraint(["signed_up_consumer_id"], ["consumers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_referral_invites_referrer_consumer_id"), "referral_invites", ["referrer_consumer_id"], unique=False)
    op.create_index(op.f("ix_referral_invites_referral_code"), "referral_invites", ["referral_code"], unique=False)
    op.create_index(op.f("ix_referral_invites_created_at"), "referral_invites", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_referral_invites_created_at"), table_name="referral_invites")
    op.drop_index(op.f("ix_referral_invites_referral_code"), table_name="referral_invites")
    op.drop_index(op.f("ix_referral_invites_referrer_consumer_id"), table_name="referral_invites")
    op.drop_table("referral_invites")

    op.drop_index(op.f("ix_marketplace_subscriptions_created_at"), table_name="marketplace_subscriptions")
    op.drop_index(op.f("ix_marketplace_subscriptions_consumer_id"), table_name="marketplace_subscriptions")
    op.drop_table("marketplace_subscriptions")
