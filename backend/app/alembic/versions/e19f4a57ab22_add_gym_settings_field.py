"""add gym settings field

Revision ID: e19f4a57ab22
Revises: c3d9b0ad1f1e
Create Date: 2026-02-18 08:20:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e19f4a57ab22"
down_revision = "c3d9b0ad1f1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "gyms",
        sa.Column(
            "settings",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'::json"),
        ),
    )


def downgrade() -> None:
    op.drop_column("gyms", "settings")
