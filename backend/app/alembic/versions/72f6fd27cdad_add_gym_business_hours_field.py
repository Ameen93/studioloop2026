"""add gym business hours field

Revision ID: 72f6fd27cdad
Revises: 2ffca2ba00f3
Create Date: 2026-02-18 06:26:28.070987

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "72f6fd27cdad"
down_revision = "2ffca2ba00f3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "gyms",
        sa.Column(
            "business_hours",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'::json"),
        ),
    )


def downgrade() -> None:
    op.drop_column("gyms", "business_hours")
