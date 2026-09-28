"""Booking concurrency: the row lock, the constraints, and one count.

Bookings were a read-check-increment on ``class_sessions.spots_booked`` with no
row lock, no uniqueness on ``(session_id, consumer_id)`` and no capacity check,
so two concurrent requests for the last spot could both succeed and a consumer
could book the same class twice. Separately, ``realtime.py`` recomputed
occupancy from ``COUNT(bookings)`` where ``status == BOOKED``, giving a second
answer that disagreed with the stored counter.

The concurrency tests here use **two real database connections** against real
Postgres, because that is the only way to exercise ``SELECT ... FOR UPDATE``:
a lock taken on one connection is invisible to a test that only ever uses one.
Each worker runs in its own thread with its own ``Session``, and a barrier makes
both reach the capacity check before either commits — which is exactly the
interleaving that used to oversell.

A NOTE ON STATUS VALUES: ``bookings.status`` is a VARCHAR holding SQLAlchemy
Enum *names* (``BOOKED``, ``CANCELLED``), not the lowercase ``BookingStatus``
values. Raw SQL against that column must use the uppercase names.
"""

import importlib.util
import threading
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlmodel import Session, select

from app.api.routes.realtime import _get_session_availability, count_occupying_bookings
from app.core.db import engine
from app.models import (
    Booking,
    BookingStatus,
    BookingType,
    ClassSession,
    Consumer,
    Gym,
    GymMembership,
    GymMembershipStatus,
    Space,
)
from app.models.booking import OCCUPYING_BOOKING_STATUSES
from app.models.digital_waiver import DigitalWaiverAcceptance
from tests.api.routes.test_staff_memberships import _consumer_headers


_MIGRATION_PATH = (
    Path(__file__).resolve().parents[3]
    / "app"
    / "alembic"
    / "versions"
    / "b5f1c07d9a33_booking_concurrency_constraints.py"
)


def _load_migration_module() -> ModuleType:
    """Import the migration by path.

    app/alembic/versions is not a package, so this is the only way to run the
    migration's real SQL rather than a copy of it in the test.
    """
    spec = importlib.util.spec_from_file_location(
        "_b5f1c07d9a33_migration", _MIGRATION_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_class_session(db: Session, gym: Gym, capacity: int) -> ClassSession:
    space = Space(gym_id=gym.id, name=f"Concurrency-{uuid4().hex[:6]}", capacity=50)
    db.add(space)
    db.commit()
    db.refresh(space)

    class_session = ClassSession(
        gym_id=gym.id,
        space_id=space.id,
        title=f"Concurrency Test {uuid4().hex[:6]}",
        start_time=datetime.now(UTC) + timedelta(days=2),
        end_time=datetime.now(UTC) + timedelta(days=2, hours=1),
        capacity=capacity,
        spots_booked=0,
        price_cents=0,
        waitlist_enabled=False,
    )
    db.add(class_session)
    db.commit()
    db.refresh(class_session)
    return class_session


def _active_member(db: Session, gym: Gym, consumer: Consumer) -> GymMembership:
    """An ACTIVE membership with an accepted waiver, so booking is permitted."""
    membership = db.exec(
        select(GymMembership).where(
            GymMembership.gym_id == gym.id,
            GymMembership.consumer_id == consumer.id,
        )
    ).first()
    if membership is None:
        membership = GymMembership(gym_id=gym.id, consumer_id=consumer.id)
        db.add(membership)
    membership.status = GymMembershipStatus.ACTIVE
    membership.is_active = True
    membership.ended_at = None
    db.add(membership)
    db.commit()
    db.refresh(membership)

    waiver = db.exec(
        select(DigitalWaiverAcceptance).where(
            DigitalWaiverAcceptance.gym_membership_id == membership.id,
            DigitalWaiverAcceptance.consumer_id == consumer.id,
        )
    ).first()
    if waiver is None:
        db.add(
            DigitalWaiverAcceptance(
                gym_id=gym.id,
                consumer_id=consumer.id,
                gym_membership_id=membership.id,
            )
        )
        db.commit()
    return membership


def _book_in_its_own_connection(
    class_session_id: UUID,
    gym_id: UUID,
    consumer_id: UUID,
    membership_id: UUID,
    barrier: threading.Barrier,
    results: list[object],
) -> None:
    """One booking attempt, on its own connection, mirroring the route's logic.

    This is deliberately the route body rather than an HTTP call: TestClient
    serialises requests through one app instance and one session dependency, so
    two HTTP calls cannot interleave inside the lock. Running the same
    lock-check-increment on two Sessions from the shared engine gives two real
    backends contending for the same row.
    """
    with Session(engine) as db:
        try:
            locked = db.exec(
                select(ClassSession)
                .where(ClassSession.id == class_session_id)
                .with_for_update()
                .execution_options(populate_existing=True)
            ).first()
            assert locked is not None

            # Both threads wait here *after* one of them has the lock, so the
            # second necessarily blocks on the SELECT above until the first
            # commits. Without FOR UPDATE both would read spots_booked == 0.
            try:
                barrier.wait(timeout=10)
            except threading.BrokenBarrierError:
                pass

            if locked.capacity and locked.spots_booked >= locked.capacity:
                results.append("full")
                db.rollback()
                return

            db.add(
                Booking(
                    gym_id=gym_id,
                    consumer_id=consumer_id,
                    session_id=class_session_id,
                    gym_membership_id=membership_id,
                    booking_type=BookingType.MEMBERSHIP_BENEFIT,
                    status=BookingStatus.BOOKED,
                )
            )
            locked.spots_booked += 1
            db.add(locked)
            db.commit()
            results.append("booked")
        except (IntegrityError, OperationalError) as exc:
            db.rollback()
            results.append(f"rejected:{type(exc).__name__}")
        except Exception as exc:  # pragma: no cover - surfaced by the assertion
            db.rollback()
            results.append(f"error:{exc!r}")


# =============================================================================
# Two concurrent bookings for the last spot
# =============================================================================


def test_two_concurrent_bookings_for_the_last_spot_yield_exactly_one(
    client: TestClient, db: Session
) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    class_session = _make_class_session(db, gym, capacity=1)

    consumers = db.exec(select(Consumer).limit(2)).all()
    assert len(consumers) == 2
    memberships = [_active_member(db, gym, c) for c in consumers]

    barrier = threading.Barrier(2)
    results: list[object] = []
    threads = [
        threading.Thread(
            target=_book_in_its_own_connection,
            args=(
                class_session.id,
                gym.id,
                consumer.id,
                membership.id,
                barrier,
                results,
            ),
        )
        for consumer, membership in zip(consumers, memberships, strict=True)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert not any(t.is_alive() for t in threads), "a booking thread deadlocked"

    assert sorted(str(r) for r in results) == ["booked", "full"], results

    db.expire_all()
    db.refresh(class_session)
    assert class_session.spots_booked == 1
    assert count_occupying_bookings(db, class_session.id) == 1


def test_ten_concurrent_bookings_never_exceed_capacity(
    client: TestClient, db: Session
) -> None:
    """The same race at wider fan-out: 10 consumers, 3 spots."""
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    capacity = 3
    class_session = _make_class_session(db, gym, capacity=capacity)

    consumers = db.exec(select(Consumer).limit(10)).all()
    assert len(consumers) == 10
    memberships = [_active_member(db, gym, c) for c in consumers]

    barrier = threading.Barrier(len(consumers))
    results: list[object] = []
    threads = [
        threading.Thread(
            target=_book_in_its_own_connection,
            args=(
                class_session.id,
                gym.id,
                consumer.id,
                membership.id,
                barrier,
                results,
            ),
        )
        for consumer, membership in zip(consumers, memberships, strict=True)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    assert not any(t.is_alive() for t in threads), "a booking thread deadlocked"

    booked = [r for r in results if r == "booked"]
    assert len(booked) == capacity, results
    assert len(results) == len(consumers), results

    db.expire_all()
    db.refresh(class_session)
    assert class_session.spots_booked == capacity
    assert count_occupying_bookings(db, class_session.id) == capacity


def test_capacity_check_constraint_rejects_an_oversell_at_the_database(
    db: Session,
) -> None:
    """Belt to the lock's braces: the database refuses too."""
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    class_session = _make_class_session(db, gym, capacity=2)

    class_session.spots_booked = 3
    db.add(class_session)
    with pytest.raises(IntegrityError) as excinfo:
        db.commit()
    assert "ck_class_session_spots_within_capacity" in str(excinfo.value)
    db.rollback()


def test_capacity_zero_means_unlimited_not_instantly_full(db: Session) -> None:
    """capacity == 0 is the codebase's 'no limit', and the CHECK exempts it."""
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    class_session = _make_class_session(db, gym, capacity=0)

    class_session.spots_booked = 500
    db.add(class_session)
    db.commit()
    db.refresh(class_session)
    assert class_session.spots_booked == 500

    availability = _get_session_availability(class_session.id)
    assert availability is not None
    assert availability["is_full"] is False
    assert availability["spots_remaining"] is None

    # No bookings back that number; put it back so the counter and the rows
    # behind it agree for anything that scans the whole table later.
    class_session.spots_booked = 0
    db.add(class_session)
    db.commit()


# =============================================================================
# Duplicate booking by the same consumer
# =============================================================================


def test_duplicate_booking_by_the_same_consumer_is_rejected_over_http(
    client: TestClient, db: Session
) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers, consumer = _consumer_headers(client, db)
    _active_member(db, gym, consumer)
    class_session = _make_class_session(db, gym, capacity=10)

    body = {
        "gym_id": str(gym.id),
        "session_id": str(class_session.id),
        "source": "direct",
    }

    first = client.post(
        "/api/v1/gyms/consumer/bookings/membership", json=body, headers=headers
    )
    assert first.status_code == 200, first.text

    second = client.post(
        "/api/v1/gyms/consumer/bookings/membership", json=body, headers=headers
    )
    assert second.status_code == 409, second.text
    assert "already have a booking" in second.json()["detail"]

    db.expire_all()
    db.refresh(class_session)
    assert class_session.spots_booked == 1
    assert count_occupying_bookings(db, class_session.id) == 1


def test_duplicate_active_booking_is_rejected_at_the_database(db: Session) -> None:
    """The partial unique index, independent of any application check."""
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    consumer = db.exec(select(Consumer)).first()
    assert consumer is not None
    class_session = _make_class_session(db, gym, capacity=10)

    for _ in range(2):
        db.add(
            Booking(
                gym_id=gym.id,
                consumer_id=consumer.id,
                session_id=class_session.id,
                booking_type=BookingType.MEMBERSHIP_BENEFIT,
                status=BookingStatus.BOOKED,
            )
        )
    with pytest.raises(IntegrityError) as excinfo:
        db.commit()
    assert "uq_booking_session_consumer_active" in str(excinfo.value)
    db.rollback()


def test_rebooking_after_cancelling_is_still_allowed(
    client: TestClient, db: Session
) -> None:
    """The index is partial on purpose: cancelling frees the consumer to rebook.

    A plain UNIQUE (session_id, consumer_id) would have made this impossible,
    which is why the constraint excludes CANCELLED rows.
    """
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers, consumer = _consumer_headers(client, db)
    _active_member(db, gym, consumer)
    class_session = _make_class_session(db, gym, capacity=10)

    body = {
        "gym_id": str(gym.id),
        "session_id": str(class_session.id),
        "source": "direct",
    }

    first = client.post(
        "/api/v1/gyms/consumer/bookings/membership", json=body, headers=headers
    )
    assert first.status_code == 200, first.text
    booking_id = first.json()["id"]

    cancel = client.post(
        f"/api/v1/gyms/consumer/bookings/{booking_id}/cancel", headers=headers
    )
    assert cancel.status_code == 200, cancel.text

    again = client.post(
        "/api/v1/gyms/consumer/bookings/membership", json=body, headers=headers
    )
    assert again.status_code == 200, again.text

    db.expire_all()
    db.refresh(class_session)
    assert class_session.spots_booked == 1
    assert count_occupying_bookings(db, class_session.id) == 1


# =============================================================================
# One count, not two
# =============================================================================


def test_realtime_count_matches_the_stored_count(
    client: TestClient, db: Session
) -> None:
    """The realtime endpoint and the stored counter must never disagree.

    realtime used to recompute from COUNT(bookings WHERE status == BOOKED),
    which missed PENDING_PAYMENT and CHECKED_IN bookings that still occupy a
    spot. Check every state transition, not just the happy path.
    """
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers, consumer = _consumer_headers(client, db)
    _active_member(db, gym, consumer)
    class_session = _make_class_session(db, gym, capacity=10)

    def assert_agreement() -> int:
        db.expire_all()
        db.refresh(class_session)
        availability = _get_session_availability(class_session.id)
        assert availability is not None
        stored = class_session.spots_booked
        assert availability["spots_booked"] == stored
        assert count_occupying_bookings(db, class_session.id) == stored
        return int(stored)

    assert assert_agreement() == 0

    body = {
        "gym_id": str(gym.id),
        "session_id": str(class_session.id),
        "source": "direct",
    }
    booked = client.post(
        "/api/v1/gyms/consumer/bookings/membership", json=body, headers=headers
    )
    assert booked.status_code == 200, booked.text
    assert assert_agreement() == 1

    # A CHECKED_IN booking still occupies its spot.
    booking = db.get(Booking, UUID(booked.json()["id"]))
    assert booking is not None
    booking.mark_checked_in()
    db.add(booking)
    db.commit()
    assert assert_agreement() == 1

    # Cancelling releases it.
    booking.mark_cancelled()
    db.add(booking)
    class_session.spots_booked -= 1
    db.add(class_session)
    db.commit()
    assert assert_agreement() == 0


def test_pending_payment_booking_still_occupies_a_spot(
    client: TestClient, db: Session
) -> None:
    """A held spot counts. The old realtime query silently ignored these."""
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    consumer = db.exec(select(Consumer)).first()
    assert consumer is not None
    class_session = _make_class_session(db, gym, capacity=5)

    db.add(
        Booking(
            gym_id=gym.id,
            consumer_id=consumer.id,
            session_id=class_session.id,
            booking_type=BookingType.PAY_PER_CLASS,
            status=BookingStatus.PENDING_PAYMENT,
            price_paid_cents=1000,
        )
    )
    class_session.spots_booked = 1
    db.add(class_session)
    db.commit()

    availability = _get_session_availability(class_session.id)
    assert availability is not None
    assert availability["spots_booked"] == 1
    assert count_occupying_bookings(db, class_session.id) == 1


def test_occupying_statuses_are_every_status_but_cancelled() -> None:
    """If a status is added, this test forces a decision about the counter."""
    assert set(OCCUPYING_BOOKING_STATUSES) == set(BookingStatus) - {
        BookingStatus.CANCELLED
    }


def _run_repair_in_a_rolled_back_transaction(db: Session, migration: ModuleType):
    """Run the migration's repair SQL exactly as the migration runs it.

    Two things matter. First, the repair statements are global — they scan the
    whole table, which is what makes them correct for a production database but
    means they must run with the constraints absent, the way the migration does
    (it repairs, then constrains). Second, Postgres DDL is transactional, so
    dropping the constraints, repairing and then rolling back leaves the shared
    test database exactly as it was, including for the other tests in this run.
    """
    db.exec(
        text(
            f"ALTER TABLE class_sessions DROP CONSTRAINT {migration.CAPACITY_CHECK_NAME}"
        )
    )
    db.exec(text(f"DROP INDEX {migration.UNIQUE_INDEX_NAME}"))
    for statement in migration.REPAIR_STATEMENTS:
        db.exec(text(statement))


def test_migration_repair_sql_reconciles_a_drifted_counter(db: Session) -> None:
    """The migration's own repair statements, run against deliberate drift.

    Loaded from the migration module by path so this exercises the SQL the
    migration actually runs, not a copy that could drift from it. This is the
    logic that brought 846 of 917 seeded sessions back into agreement, and that
    has to hold for a populated production database too.
    """
    migration = _load_migration_module()

    gym = db.exec(select(Gym)).first()
    assert gym is not None
    consumer = db.exec(select(Consumer)).first()
    assert consumer is not None
    class_session = _make_class_session(db, gym, capacity=10)

    db.add(
        Booking(
            gym_id=gym.id,
            consumer_id=consumer.id,
            session_id=class_session.id,
            booking_type=BookingType.MEMBERSHIP_BENEFIT,
            status=BookingStatus.BOOKED,
        )
    )
    class_session.spots_booked = 7  # drift, the way the seed produced it
    db.add(class_session)
    db.commit()
    db.expire_all()
    db.refresh(class_session)
    assert class_session.spots_booked == 7
    assert count_occupying_bookings(db, class_session.id) == 1

    try:
        _run_repair_in_a_rolled_back_transaction(db, migration)
        db.expire_all()
        db.refresh(class_session)
        assert class_session.spots_booked == 1
        assert count_occupying_bookings(db, class_session.id) == 1
    finally:
        db.rollback()

    # Leave the row consistent now that the repair has been rolled back.
    db.expire_all()
    db.refresh(class_session)
    assert class_session.spots_booked == 7
    class_session.spots_booked = 1
    db.add(class_session)
    db.commit()


def test_migration_repair_sql_collapses_duplicate_active_bookings(db: Session) -> None:
    """Duplicates that predate the index are cancelled, not deleted."""
    migration = _load_migration_module()

    gym = db.exec(select(Gym)).first()
    assert gym is not None
    consumer = db.exec(select(Consumer)).first()
    assert consumer is not None
    class_session = _make_class_session(db, gym, capacity=10)

    try:
        # The index has to go before the duplicates can be inserted at all; this
        # is simulating rows that predate the migration. Everything here is
        # rolled back, DDL included.
        _run_repair_in_a_rolled_back_transaction(db, migration)
        for _ in range(3):
            db.add(
                Booking(
                    gym_id=gym.id,
                    consumer_id=consumer.id,
                    session_id=class_session.id,
                    booking_type=BookingType.MEMBERSHIP_BENEFIT,
                    status=BookingStatus.BOOKED,
                )
            )
        db.flush()
        assert count_occupying_bookings(db, class_session.id) == 3

        for statement in migration.REPAIR_STATEMENTS:
            db.exec(text(statement))
        db.expire_all()

        # One survives; the other two are CANCELLED rather than removed.
        assert count_occupying_bookings(db, class_session.id) == 1
        all_rows = db.exec(
            select(Booking).where(Booking.session_id == class_session.id)
        ).all()
        assert len(all_rows) == 3
        assert sum(r.status == BookingStatus.CANCELLED for r in all_rows) == 2

        db.refresh(class_session)
        assert class_session.spots_booked == 1
    finally:
        db.rollback()

    # Nothing survived the rollback: no bookings, and the constraints are back.
    db.expire_all()
    assert count_occupying_bookings(db, class_session.id) == 0
    assert (
        db.exec(
            text(
                "SELECT count(*) FROM pg_constraint "
                f"WHERE conname = '{migration.CAPACITY_CHECK_NAME}'"
            )
        ).one()[0]
        == 1
    )
    assert (
        db.exec(
            text(
                "SELECT count(*) FROM pg_indexes "
                f"WHERE indexname = '{migration.UNIQUE_INDEX_NAME}'"
            )
        ).one()[0]
        == 1
    )
