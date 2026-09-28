"""booking concurrency constraints

Revision ID: b5f1c07d9a33
Revises: a1b2c3d4e5f6
Create Date: 2026-09-28 00:00:00.000000

Bookings were a read-check-increment on class_sessions.spots_booked with no row
lock, no uniqueness and no capacity constraint, so two concurrent requests for
the last spot could both succeed and one consumer could book the same class
twice. The application now takes SELECT ... FOR UPDATE around the check and the
increment; this migration puts the same invariants in the database, where they
hold regardless of which code path writes.

Three things are added:

1. ``uq_booking_session_consumer_active`` — a PARTIAL unique index on
   ``(session_id, consumer_id)`` covering every status except ``CANCELLED``. It
   is partial on purpose: a plain unique constraint would stop a consumer ever
   re-booking a class they had cancelled, which is a legitimate flow the
   cancel endpoint supports. "One *active* booking per consumer per session" is
   the invariant that was actually missing.

2. ``ck_class_session_spots_within_capacity`` — ``spots_booked`` may not exceed
   ``capacity``, and may not go negative. ``capacity = 0`` means unlimited
   throughout this codebase (see ``book_with_membership`` and ``join_waitlist``,
   which both treat a falsy capacity as no limit), so the check exempts it.

3. A reconciliation of ``spots_booked`` against ``COUNT(bookings)``. These were
   two disagreeing sources of truth — in the seeded database 846 of 917 sessions
   disagreed — and ``spots_booked`` is now the single source of truth, so it is
   recomputed here from the bookings that back it.

A NOTE ON STATUS VALUES: ``bookings.status`` is a VARCHAR(20) holding
SQLAlchemy Enum *names*, which are UPPERCASE (``BOOKED``, ``CANCELLED``,
``CHECKED_IN``, ``PENDING_PAYMENT``), not the lowercase ``BookingStatus`` enum
*values*. Raw SQL against this column must use the uppercase names.

Existing rows are repaired before the constraints go on, so this migration is
safe to run against a populated database:

* duplicate active bookings are collapsed to the earliest one, the rest
  cancelled rather than deleted, so nothing is lost;
* ``spots_booked`` is recomputed, then clamped to ``capacity``.

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b5f1c07d9a33'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


UNIQUE_INDEX_NAME = 'uq_booking_session_consumer_active'
CAPACITY_CHECK_NAME = 'ck_class_session_spots_within_capacity'

# Every status that occupies a spot. A PENDING_PAYMENT booking holds its spot
# while payment clears, and a CHECKED_IN booking obviously still occupies one;
# only CANCELLED releases it.
ACTIVE_STATUSES_SQL = "('PENDING_PAYMENT', 'BOOKED', 'CHECKED_IN')"


# The repair statements are module-level constants so the test suite can run the
# exact SQL this migration runs, instead of a copy of it that could drift.
# See tests/api/routes/test_booking_concurrency.py.

# Keep the earliest active booking for each (session_id, consumer_id) and cancel
# the rest. Cancelling rather than deleting keeps the history and matches what
# the application would have done.
COLLAPSE_DUPLICATE_BOOKINGS_SQL = f"""
    WITH ranked AS (
        SELECT id,
               row_number() OVER (
                   PARTITION BY session_id, consumer_id
                   ORDER BY created_at, id
               ) AS rn
        FROM bookings
        WHERE status IN {ACTIVE_STATUSES_SQL}
    )
    UPDATE bookings b
       SET status = 'CANCELLED',
           cancelled_at = COALESCE(b.cancelled_at, now())
      FROM ranked r
     WHERE b.id = r.id
       AND r.rn > 1;
"""

# Make spots_booked agree with the bookings behind it.
RECONCILE_SPOTS_BOOKED_SQL = f"""
    UPDATE class_sessions cs
       SET spots_booked = sub.actual
      FROM (
            SELECT cs2.id,
                   (SELECT count(*)
                      FROM bookings b
                     WHERE b.session_id = cs2.id
                       AND b.status IN {ACTIVE_STATUSES_SQL}) AS actual
              FROM class_sessions cs2
           ) AS sub
     WHERE cs.id = sub.id
       AND cs.spots_booked IS DISTINCT FROM sub.actual;
"""

# Clamp anything the reconciliation pushed past capacity. Oversold classes
# predate the lock; there is no correct answer for which booking to drop, so the
# counter is brought to the limit and the bookings are left for a human.
CLAMP_SPOTS_BOOKED_SQL = """
    UPDATE class_sessions
       SET spots_booked = capacity
     WHERE capacity > 0
       AND spots_booked > capacity;
"""

FLOOR_SPOTS_BOOKED_SQL = """
    UPDATE class_sessions SET spots_booked = 0 WHERE spots_booked < 0;
"""

# Applied in order: duplicates first (they change the counts), then the counts,
# then the bounds.
REPAIR_STATEMENTS = (
    COLLAPSE_DUPLICATE_BOOKINGS_SQL,
    RECONCILE_SPOTS_BOOKED_SQL,
    CLAMP_SPOTS_BOOKED_SQL,
    FLOOR_SPOTS_BOOKED_SQL,
)


def upgrade():
    # --- repair existing rows so the constraints below can be added ---------
    for statement in REPAIR_STATEMENTS:
        op.execute(sa.text(statement))

    # --- constraints --------------------------------------------------------
    op.create_index(
        UNIQUE_INDEX_NAME,
        'bookings',
        ['session_id', 'consumer_id'],
        unique=True,
        postgresql_where=sa.text("status <> 'CANCELLED'"),
    )

    op.create_check_constraint(
        CAPACITY_CHECK_NAME,
        'class_sessions',
        'spots_booked >= 0 AND (capacity = 0 OR spots_booked <= capacity)',
    )


def downgrade():
    op.drop_constraint(CAPACITY_CHECK_NAME, 'class_sessions', type_='check')
    op.drop_index(UNIQUE_INDEX_NAME, table_name='bookings')
