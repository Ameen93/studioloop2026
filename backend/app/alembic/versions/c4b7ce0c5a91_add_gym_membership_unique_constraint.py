"""add_gym_membership_unique_constraint

Revision ID: c4b7ce0c5a91
Revises: aa2c9f03c120
Create Date: 2026-02-18 09:55:00.000000

Offline note: this migration used to call ``sa.inspect(op.get_bind())`` to ask
whether the constraint already existed. In offline (``--sql``) mode the bind is
a ``MockConnection`` with no database behind it, so that raised
``NoInspectionAvailable`` and broke ``alembic upgrade head --sql`` for the whole
chain. The existence check is now expressed as SQL that Postgres evaluates
itself, so the same statement is correct whether it is executed against a live
connection or merely emitted into a script.

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c4b7ce0c5a91'
down_revision = 'aa2c9f03c120'
branch_labels = None
depends_on = None


CONSTRAINT_NAME = 'uq_gym_membership_gym_consumer'


def upgrade():
    # ADD CONSTRAINT has no IF NOT EXISTS, so guard with a DO block that asks
    # the catalogue. Idempotent, and valid online and offline alike.
    op.execute(
        sa.text(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = '{CONSTRAINT_NAME}'
                      AND conrelid = 'gym_memberships'::regclass
                ) THEN
                    ALTER TABLE gym_memberships
                        ADD CONSTRAINT {CONSTRAINT_NAME}
                        UNIQUE (gym_id, consumer_id);
                END IF;
            END $$;
            """
        )
    )


def downgrade():
    op.execute(
        sa.text(
            f"ALTER TABLE gym_memberships "
            f"DROP CONSTRAINT IF EXISTS {CONSTRAINT_NAME};"
        )
    )
