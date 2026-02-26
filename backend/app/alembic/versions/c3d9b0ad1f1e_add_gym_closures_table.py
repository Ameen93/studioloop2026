"""add gym closures table

Revision ID: c3d9b0ad1f1e
Revises: 72f6fd27cdad
Create Date: 2026-02-18 07:58:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c3d9b0ad1f1e"
down_revision = "72f6fd27cdad"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "gym_closures",
        sa.Column("closure_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("gym_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["gym_id"], ["gyms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("gym_id", "closure_date", name="uq_gym_closures_gym_date"),
    )
    op.create_index(op.f("ix_gym_closures_created_at"), "gym_closures", ["created_at"], unique=False)
    op.create_index(op.f("ix_gym_closures_gym_id"), "gym_closures", ["gym_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_gym_closures_gym_id"), table_name="gym_closures")
    op.drop_index(op.f("ix_gym_closures_created_at"), table_name="gym_closures")
    op.drop_table("gym_closures")
