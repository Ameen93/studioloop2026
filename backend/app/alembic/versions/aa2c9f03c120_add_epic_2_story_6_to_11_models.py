"""add_epic_2_story_6_to_11_models

Revision ID: aa2c9f03c120
Revises: e19f4a57ab22
Create Date: 2026-02-18 09:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'aa2c9f03c120'
down_revision = 'e19f4a57ab22'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('gyms', sa.Column('subscription_tier', sa.String(length=20), nullable=False, server_default='starter'))

    op.add_column('spaces', sa.Column('amenities', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('spaces', sa.Column('equipment', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('spaces', sa.Column('custom_amenities', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('spaces', sa.Column('custom_equipment', sa.JSON(), nullable=False, server_default='[]'))

    op.create_table(
        'class_sessions',
        sa.Column('space_id', sa.Uuid(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('gym_id', sa.Uuid(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['gym_id'], ['gyms.id']),
        sa.ForeignKeyConstraint(['space_id'], ['spaces.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_class_sessions_created_at'), 'class_sessions', ['created_at'], unique=False)
    op.create_index(op.f('ix_class_sessions_gym_id'), 'class_sessions', ['gym_id'], unique=False)
    op.create_index(op.f('ix_class_sessions_is_active'), 'class_sessions', ['is_active'], unique=False)
    op.create_index(op.f('ix_class_sessions_space_id'), 'class_sessions', ['space_id'], unique=False)

    op.create_table(
        'gym_memberships',
        sa.Column('gym_id', sa.Uuid(), nullable=False),
        sa.Column('consumer_id', sa.Uuid(), nullable=False),
        sa.Column('membership_tier', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['consumer_id'], ['consumers.id']),
        sa.ForeignKeyConstraint(['gym_id'], ['gyms.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_gym_memberships_consumer_id'), 'gym_memberships', ['consumer_id'], unique=False)
    op.create_index(op.f('ix_gym_memberships_created_at'), 'gym_memberships', ['created_at'], unique=False)
    op.create_index(op.f('ix_gym_memberships_gym_id'), 'gym_memberships', ['gym_id'], unique=False)
    op.create_index(op.f('ix_gym_memberships_is_active'), 'gym_memberships', ['is_active'], unique=False)
    op.create_unique_constraint('uq_gym_membership_gym_consumer', 'gym_memberships', ['gym_id', 'consumer_id'])


def downgrade():
    op.drop_constraint('uq_gym_membership_gym_consumer', 'gym_memberships', type_='unique')
    op.drop_index(op.f('ix_gym_memberships_is_active'), table_name='gym_memberships')
    op.drop_index(op.f('ix_gym_memberships_gym_id'), table_name='gym_memberships')
    op.drop_index(op.f('ix_gym_memberships_created_at'), table_name='gym_memberships')
    op.drop_index(op.f('ix_gym_memberships_consumer_id'), table_name='gym_memberships')
    op.drop_table('gym_memberships')

    op.drop_index(op.f('ix_class_sessions_space_id'), table_name='class_sessions')
    op.drop_index(op.f('ix_class_sessions_is_active'), table_name='class_sessions')
    op.drop_index(op.f('ix_class_sessions_gym_id'), table_name='class_sessions')
    op.drop_index(op.f('ix_class_sessions_created_at'), table_name='class_sessions')
    op.drop_table('class_sessions')

    op.drop_column('spaces', 'custom_equipment')
    op.drop_column('spaces', 'custom_amenities')
    op.drop_column('spaces', 'equipment')
    op.drop_column('spaces', 'amenities')

    op.drop_column('gyms', 'subscription_tier')
