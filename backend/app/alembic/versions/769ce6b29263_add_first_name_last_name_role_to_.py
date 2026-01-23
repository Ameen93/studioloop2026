"""add_first_name_last_name_role_to_consumers

Revision ID: 769ce6b29263
Revises: 35691627cac5
Create Date: 2026-01-23 09:26:17.419620

Adds first_name, last_name, and role columns to consumers table.
Migrates existing full_name data to first_name/last_name.
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '769ce6b29263'
down_revision = '35691627cac5'
branch_labels = None
depends_on = None


def upgrade():
    # Create the enum type first
    userrole = sa.Enum('CONSUMER', 'OWNER', 'MANAGER', 'FRONT_DESK', 'INSTRUCTOR', name='userrole')
    userrole.create(op.get_bind(), checkfirst=True)

    # Add columns as nullable first
    op.add_column('consumers', sa.Column('first_name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True))
    op.add_column('consumers', sa.Column('last_name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True))
    op.add_column('consumers', sa.Column('role', userrole, nullable=True))

    # Migrate existing data: split full_name into first_name/last_name
    # If full_name exists, use first word as first_name, rest as last_name
    # Default role to CONSUMER
    op.execute("""
        UPDATE consumers
        SET
            first_name = COALESCE(
                SPLIT_PART(full_name, ' ', 1),
                'Unknown'
            ),
            last_name = COALESCE(
                CASE
                    WHEN POSITION(' ' IN full_name) > 0
                    THEN SUBSTRING(full_name FROM POSITION(' ' IN full_name) + 1)
                    ELSE 'User'
                END,
                'User'
            ),
            role = 'CONSUMER'
        WHERE first_name IS NULL OR last_name IS NULL OR role IS NULL
    """)

    # Now make columns non-nullable
    op.alter_column('consumers', 'first_name', nullable=False)
    op.alter_column('consumers', 'last_name', nullable=False)
    op.alter_column('consumers', 'role', nullable=False)


def downgrade():
    op.drop_column('consumers', 'role')
    op.drop_column('consumers', 'last_name')
    op.drop_column('consumers', 'first_name')

    # Drop the enum type
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
