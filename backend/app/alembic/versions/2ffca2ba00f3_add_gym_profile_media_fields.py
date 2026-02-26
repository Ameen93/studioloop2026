"""add gym profile media fields

Revision ID: 2ffca2ba00f3
Revises: 3b27541620fc
Create Date: 2026-02-18 06:20:07.325080

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2ffca2ba00f3"
down_revision = "3b27541620fc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("gyms", sa.Column("tagline", sa.String(length=180), nullable=True))
    op.add_column("gyms", sa.Column("logo_url", sa.String(length=2048), nullable=True))
    op.add_column(
        "gyms",
        sa.Column(
            "cover_photo_urls",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )


def downgrade() -> None:
    op.drop_column("gyms", "cover_photo_urls")
    op.drop_column("gyms", "logo_url")
    op.drop_column("gyms", "tagline")
