"""payment state machine: add pending_payment states and nullable gym_id on payments

Revision ID: a1b2c3d4e5f6
Revises: e908912874a5
Create Date: 2026-03-17

Adds PENDING_PAYMENT status to gym_memberships, bookings, and
marketplace_subscriptions (string columns, no DDL needed).
Makes payments.gym_id nullable for platform-level payments
(marketplace subscriptions have no associated gym).
"""

from alembic import op


revision = "a1b2c3d4e5f6"
down_revision = "e908912874a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("payments", "gym_id", nullable=True)


def downgrade() -> None:
    # Will fail if any NULL gym_id rows exist
    op.alter_column("payments", "gym_id", nullable=False)
