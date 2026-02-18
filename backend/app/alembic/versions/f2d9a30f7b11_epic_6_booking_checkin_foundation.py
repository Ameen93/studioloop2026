"""epic 6 booking and check-in foundation

Revision ID: f2d9a30f7b11
Revises: a7c9d2e4b123
Create Date: 2026-02-18 10:50:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f2d9a30f7b11"
down_revision = "a7c9d2e4b123"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("class_sessions") as batch_op:
        batch_op.add_column(sa.Column("capacity", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("spots_booked", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("waitlist_enabled", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column("price_cents", sa.Integer(), nullable=False, server_default="0"))

    op.create_table(
        "bookings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("gym_id", sa.Uuid(), nullable=False),
        sa.Column("consumer_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("gym_membership_id", sa.Uuid(), nullable=True),
        sa.Column("booking_type", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("price_paid_cents", sa.Integer(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("checked_in_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_refunded", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["consumer_id"], ["consumers.id"]),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.id"]),
        sa.ForeignKeyConstraint(["gym_membership_id"], ["gym_memberships.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["class_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bookings_created_at"), "bookings", ["created_at"], unique=False)
    op.create_index(op.f("ix_bookings_consumer_id"), "bookings", ["consumer_id"], unique=False)
    op.create_index(op.f("ix_bookings_gym_id"), "bookings", ["gym_id"], unique=False)
    op.create_index(op.f("ix_bookings_session_id"), "bookings", ["session_id"], unique=False)

    op.create_table(
        "waitlist_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("gym_id", sa.Uuid(), nullable=False),
        sa.Column("consumer_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("offered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["consumer_id"], ["consumers.id"]),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["class_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_waitlist_entries_created_at"), "waitlist_entries", ["created_at"], unique=False)
    op.create_index(op.f("ix_waitlist_entries_consumer_id"), "waitlist_entries", ["consumer_id"], unique=False)
    op.create_index(op.f("ix_waitlist_entries_gym_id"), "waitlist_entries", ["gym_id"], unique=False)
    op.create_index(op.f("ix_waitlist_entries_session_id"), "waitlist_entries", ["session_id"], unique=False)

    op.create_table(
        "check_in_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("gym_id", sa.Uuid(), nullable=False),
        sa.Column("consumer_id", sa.Uuid(), nullable=False),
        sa.Column("booking_id", sa.Uuid(), nullable=True),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("checked_in_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("offline_recorded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.ForeignKeyConstraint(["consumer_id"], ["consumers.id"]),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_check_in_records_created_at"), "check_in_records", ["created_at"], unique=False)
    op.create_index(op.f("ix_check_in_records_consumer_id"), "check_in_records", ["consumer_id"], unique=False)
    op.create_index(op.f("ix_check_in_records_gym_id"), "check_in_records", ["gym_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_check_in_records_gym_id"), table_name="check_in_records")
    op.drop_index(op.f("ix_check_in_records_consumer_id"), table_name="check_in_records")
    op.drop_index(op.f("ix_check_in_records_created_at"), table_name="check_in_records")
    op.drop_table("check_in_records")

    op.drop_index(op.f("ix_waitlist_entries_session_id"), table_name="waitlist_entries")
    op.drop_index(op.f("ix_waitlist_entries_gym_id"), table_name="waitlist_entries")
    op.drop_index(op.f("ix_waitlist_entries_consumer_id"), table_name="waitlist_entries")
    op.drop_index(op.f("ix_waitlist_entries_created_at"), table_name="waitlist_entries")
    op.drop_table("waitlist_entries")

    op.drop_index(op.f("ix_bookings_session_id"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_gym_id"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_consumer_id"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_created_at"), table_name="bookings")
    op.drop_table("bookings")

    with op.batch_alter_table("class_sessions") as batch_op:
        batch_op.drop_column("price_cents")
        batch_op.drop_column("waitlist_enabled")
        batch_op.drop_column("spots_booked")
        batch_op.drop_column("capacity")
