"""add_gym_membership_unique_constraint

Revision ID: c4b7ce0c5a91
Revises: aa2c9f03c120
Create Date: 2026-02-18 09:55:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c4b7ce0c5a91'
down_revision = 'aa2c9f03c120'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        'uq_gym_membership_gym_consumer',
        'gym_memberships',
        ['gym_id', 'consumer_id'],
    )


def downgrade():
    op.drop_constraint('uq_gym_membership_gym_consumer', 'gym_memberships', type_='unique')
