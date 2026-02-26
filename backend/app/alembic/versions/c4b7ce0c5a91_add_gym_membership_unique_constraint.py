"""add_gym_membership_unique_constraint

Revision ID: c4b7ce0c5a91
Revises: aa2c9f03c120
Create Date: 2026-02-18 09:55:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c4b7ce0c5a91'
down_revision = 'aa2c9f03c120'
branch_labels = None
depends_on = None


CONSTRAINT_NAME = 'uq_gym_membership_gym_consumer'


def _has_unique_constraint(name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    uniques = inspector.get_unique_constraints('gym_memberships')
    return any(constraint.get('name') == name for constraint in uniques)


def upgrade():
    if not _has_unique_constraint(CONSTRAINT_NAME):
        op.create_unique_constraint(
            CONSTRAINT_NAME,
            'gym_memberships',
            ['gym_id', 'consumer_id'],
        )


def downgrade():
    if _has_unique_constraint(CONSTRAINT_NAME):
        op.drop_constraint(CONSTRAINT_NAME, 'gym_memberships', type_='unique')
