"""add epic 3 and 4 models

Revision ID: f3b4d6e8a901
Revises: c4b7ce0c5a91
Create Date: 2026-02-18 09:40:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f3b4d6e8a901"
down_revision: str | None = "c4b7ce0c5a91"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("staff", sa.Column("invitation_status", sa.String(length=20), nullable=False, server_default="accepted"))
    op.add_column("staff", sa.Column("working_hours", postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default="{}"))
    op.add_column("staff", sa.Column("hourly_rate_cents", sa.Integer(), nullable=True))

    op.add_column("class_sessions", sa.Column("instructor_staff_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_class_sessions_instructor_staff_id",
        "class_sessions",
        "staff",
        ["instructor_staff_id"],
        ["id"],
    )

    op.create_table(
        "membership_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("gym_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("billing_cycle", sa.String(length=20), nullable=False),
        sa.Column("benefits", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("usage_limits", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("rules", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("waiver_text", sa.String(length=5000), nullable=True),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_membership_plans_gym_id"), "membership_plans", ["gym_id"], unique=False)
    op.create_index(op.f("ix_membership_plans_is_active"), "membership_plans", ["is_active"], unique=False)

    op.add_column("gym_memberships", sa.Column("membership_plan_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("gym_memberships", sa.Column("payment_method_last4", sa.String(length=4), nullable=True))
    op.add_column("gym_memberships", sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
    op.add_column("gym_memberships", sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        "fk_gym_memberships_membership_plan_id",
        "gym_memberships",
        "membership_plans",
        ["membership_plan_id"],
        ["id"],
    )
    op.create_index(op.f("ix_gym_memberships_membership_plan_id"), "gym_memberships", ["membership_plan_id"], unique=False)

    op.create_table(
        "digital_waiver_acceptances",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("gym_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("consumer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("gym_membership_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("waiver_version", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["consumer_id"], ["consumers.id"]),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.id"]),
        sa.ForeignKeyConstraint(["gym_membership_id"], ["gym_memberships.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_digital_waiver_acceptances_consumer_id"), "digital_waiver_acceptances", ["consumer_id"], unique=False)
    op.create_index(op.f("ix_digital_waiver_acceptances_gym_id"), "digital_waiver_acceptances", ["gym_id"], unique=False)
    op.create_index(op.f("ix_digital_waiver_acceptances_gym_membership_id"), "digital_waiver_acceptances", ["gym_membership_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_digital_waiver_acceptances_gym_membership_id"), table_name="digital_waiver_acceptances")
    op.drop_index(op.f("ix_digital_waiver_acceptances_gym_id"), table_name="digital_waiver_acceptances")
    op.drop_index(op.f("ix_digital_waiver_acceptances_consumer_id"), table_name="digital_waiver_acceptances")
    op.drop_table("digital_waiver_acceptances")

    op.drop_index(op.f("ix_gym_memberships_membership_plan_id"), table_name="gym_memberships")
    op.drop_constraint("fk_gym_memberships_membership_plan_id", "gym_memberships", type_="foreignkey")
    op.drop_column("gym_memberships", "ended_at")
    op.drop_column("gym_memberships", "started_at")
    op.drop_column("gym_memberships", "payment_method_last4")
    op.drop_column("gym_memberships", "membership_plan_id")

    op.drop_index(op.f("ix_membership_plans_is_active"), table_name="membership_plans")
    op.drop_index(op.f("ix_membership_plans_gym_id"), table_name="membership_plans")
    op.drop_table("membership_plans")

    op.drop_constraint("fk_class_sessions_instructor_staff_id", "class_sessions", type_="foreignkey")
    op.drop_column("class_sessions", "instructor_staff_id")

    op.drop_column("staff", "hourly_rate_cents")
    op.drop_column("staff", "working_hours")
    op.drop_column("staff", "invitation_status")
