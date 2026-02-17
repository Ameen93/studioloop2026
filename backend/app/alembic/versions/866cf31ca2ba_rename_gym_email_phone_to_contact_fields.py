"""rename_gym_email_phone_to_contact_fields

Revision ID: 866cf31ca2ba
Revises: 3b27541620fc
Create Date: 2026-01-24 15:27:29.964673

Story 2.1: Rename gyms.email -> contact_email and gyms.phone -> contact_phone
per AC #5 which requires explicit contact_email and contact_phone field names.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '866cf31ca2ba'
down_revision = '3b27541620fc'
branch_labels = None
depends_on = None


def upgrade():
    # Rename email to contact_email (preserves existing data)
    op.alter_column('gyms', 'email', new_column_name='contact_email')
    # Rename phone to contact_phone (preserves existing data)
    op.alter_column('gyms', 'phone', new_column_name='contact_phone')


def downgrade():
    # Rename back to original names
    op.alter_column('gyms', 'contact_email', new_column_name='email')
    op.alter_column('gyms', 'contact_phone', new_column_name='phone')
