"""add_gym_profile_fields_tagline_logo_photos

Revision ID: b39ef91be31a
Revises: 866cf31ca2ba
Create Date: 2026-01-25 07:42:39.506811

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'b39ef91be31a'
down_revision = '866cf31ca2ba'
branch_labels = None
depends_on = None


def upgrade():
    # Add new gym profile fields for Story 2.2
    op.add_column('gyms', sa.Column('tagline', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=True))
    op.add_column('gyms', sa.Column('logo_url', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True))
    op.add_column('gyms', sa.Column('photo_urls', sa.JSON(), nullable=False, server_default='[]'))


def downgrade():
    op.drop_column('gyms', 'photo_urls')
    op.drop_column('gyms', 'logo_url')
    op.drop_column('gyms', 'tagline')
