"""POPIA deletion worker (M24).

Permanently deletes consumer data after the 30-day grace period.
Run via: uv run python scripts/cleanup_deleted_accounts.py [--dry-run]
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

# Ensure app modules are importable
sys.path.insert(0, ".")

from app.core.db import engine  # noqa: E402
from app.models import (  # noqa: E402
    Booking,
    CheckInRecord,
    Consumer,
    GymMembership,
    MarketplaceSubscription,
    Payment,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

GRACE_PERIOD_DAYS = 30


def cleanup_deleted_accounts(dry_run: bool = False) -> int:
    """Find and permanently delete consumer accounts past the grace period."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=GRACE_PERIOD_DAYS)

    with Session(engine) as session:
        stmt = select(Consumer).where(
            Consumer.deletion_requested_at != None,  # noqa: E711
            Consumer.deletion_requested_at < cutoff,
            Consumer.is_active == False,  # noqa: E712
        )
        consumers = session.exec(stmt).all()

        if not consumers:
            logger.info("No accounts to clean up.")
            return 0

        logger.info(
            "Found %d account(s) past %d-day grace period.",
            len(consumers),
            GRACE_PERIOD_DAYS,
        )

        deleted_count = 0
        for consumer in consumers:
            logger.info(
                "Processing consumer %s (deletion requested %s)",
                consumer.id,
                consumer.deletion_requested_at,
            )

            if dry_run:
                logger.info("[DRY RUN] Would delete consumer %s", consumer.id)
                deleted_count += 1
                continue

            # Delete bookings
            bookings = session.exec(
                select(Booking).where(Booking.consumer_id == consumer.id)
            ).all()
            for booking in bookings:
                session.delete(booking)
            logger.info("  Deleted %d bookings", len(bookings))

            # Delete check-in records
            check_ins = session.exec(
                select(CheckInRecord).where(CheckInRecord.consumer_id == consumer.id)
            ).all()
            for ci in check_ins:
                session.delete(ci)
            logger.info("  Deleted %d check-in records", len(check_ins))

            # Delete gym memberships
            memberships = session.exec(
                select(GymMembership).where(GymMembership.consumer_id == consumer.id)
            ).all()
            for m in memberships:
                session.delete(m)
            logger.info("  Deleted %d memberships", len(memberships))

            # Delete marketplace subscriptions
            subs = session.exec(
                select(MarketplaceSubscription).where(
                    MarketplaceSubscription.consumer_id == consumer.id
                )
            ).all()
            for s in subs:
                session.delete(s)
            logger.info("  Deleted %d subscriptions", len(subs))

            # Anonymize payments (keep for financial records, null out PII)
            payments = session.exec(
                select(Payment).where(Payment.consumer_id == consumer.id)
            ).all()
            for p in payments:
                p.consumer_id = None  # type: ignore[assignment]
            logger.info("  Anonymized %d payments", len(payments))

            # Delete consumer record
            session.delete(consumer)
            deleted_count += 1
            logger.info("  Deleted consumer %s", consumer.id)

        if not dry_run:
            session.commit()

        logger.info(
            "%s %d consumer account(s).",
            "Would delete" if dry_run else "Deleted",
            deleted_count,
        )
        return deleted_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="POPIA account cleanup worker")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log what would be deleted without making changes",
    )
    args = parser.parse_args()
    cleanup_deleted_accounts(dry_run=args.dry_run)
