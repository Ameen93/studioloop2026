"""add tier to membership plans

Revision ID: a7c9d2e4b123
Revises: f3b4d6e8a901
Create Date: 2026-02-18 09:55:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a7c9d2e4b123"
down_revision: str | None = "f3b4d6e8a901"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "membership_plans",
        sa.Column("tier", sa.String(length=20), nullable=False, server_default="basic"),
    )


def downgrade() -> None:
    op.drop_column("membership_plans", "tier")
