"""Seed data for Payment entities.

Creates realistic payment records for memberships and class bookings.
Uses SA payment providers (Ozow, PayFast) with ZAR currency.
"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.models import (
    Booking,
    GymMembership,
    MembershipPlan,
    Payment,
)
from app.models.booking import BookingType
from app.models.gym_membership import GymMembershipStatus
from app.models.payment import PaymentProviderName, PaymentStatus, PaymentType


def seed_payments(session: Session) -> int:
    """Seed payment records idempotently.

    Creates payments for:
    1. Membership sign-ups (one payment per active/inactive membership)
    2. Pay-per-class bookings (one payment per PAY_PER_CLASS booking)
    3. A few failed/refunded payments for realism

    Provider split: 70% Ozow, 30% PayFast
    Status: ~80% completed, ~10% failed, ~5% refunded, ~5% pending

    Args:
        session: SQLModel database session

    Returns:
        Number of payments created/found
    """
    existing = session.exec(select(Payment.id)).all()
    if len(existing) > 0:
        return len(existing)

    now = datetime.now(timezone.utc)
    count = 0

    # --- Membership payments ---
    memberships = session.exec(select(GymMembership)).all()
    plans_by_id: dict[str, MembershipPlan] = {}
    all_plans = session.exec(select(MembershipPlan)).all()
    for p in all_plans:
        plans_by_id[str(p.id)] = p

    for i, membership in enumerate(memberships):
        plan = plans_by_id.get(str(membership.membership_plan_id))
        if not plan:
            continue

        started = membership.started_at
        if started and started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)

        provider = (
            PaymentProviderName.OZOW if i % 10 < 7 else PaymentProviderName.PAYFAST
        )

        # Most membership payments succeed
        if membership.status == GymMembershipStatus.ACTIVE:
            status = PaymentStatus.COMPLETED
            completed_at = started + timedelta(minutes=2) if started else now
            failed_at = None
            failure_reason = None
        elif membership.status == GymMembershipStatus.CANCELLED:
            # Some cancelled memberships had refunds
            if i % 4 == 0:
                status = PaymentStatus.REFUNDED
                completed_at = started + timedelta(minutes=2) if started else now
                failed_at = None
                failure_reason = None
            else:
                status = PaymentStatus.COMPLETED
                completed_at = started + timedelta(minutes=2) if started else now
                failed_at = None
                failure_reason = None
        else:
            status = PaymentStatus.COMPLETED
            completed_at = started + timedelta(minutes=2) if started else now
            failed_at = None
            failure_reason = None

        payment = Payment(
            gym_id=membership.gym_id,
            consumer_id=membership.consumer_id,
            amount_cents=plan.price_cents,
            currency="ZAR",
            payment_type=PaymentType.MEMBERSHIP,
            status=status,
            provider=provider,
            provider_reference=f"OZW-{uuid.uuid4().hex[:12].upper()}"
            if provider == PaymentProviderName.OZOW
            else f"PF-{uuid.uuid4().hex[:10].upper()}",
            description=f"{plan.name} membership at {membership.gym_id}",
            related_entity_id=membership.id,
            completed_at=completed_at,
            failed_at=failed_at,
            failure_reason=failure_reason,
            refunded_at=completed_at + timedelta(days=5)
            if status == PaymentStatus.REFUNDED
            else None,
        )
        session.add(payment)
        count += 1

    # --- Class booking payments (pay-per-class only) ---
    ppc_bookings = session.exec(
        select(Booking).where(
            Booking.booking_type == BookingType.PAY_PER_CLASS,
            Booking.price_paid_cents > 0,
        )
    ).all()

    for i, booking in enumerate(ppc_bookings):
        provider = (
            PaymentProviderName.OZOW if i % 10 < 7 else PaymentProviderName.PAYFAST
        )

        # Status distribution for class payments
        roll = i % 20
        if roll < 16:
            status = PaymentStatus.COMPLETED
            completed_at = booking.created_at
            if completed_at and completed_at.tzinfo is None:
                completed_at = completed_at.replace(tzinfo=timezone.utc)
            completed_at = completed_at + timedelta(minutes=1) if completed_at else now
            failed_at = None
            failure_reason = None
        elif roll < 18:
            status = PaymentStatus.FAILED
            completed_at = None
            created = booking.created_at
            if created and created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            failed_at = created + timedelta(seconds=30) if created else now
            failure_reason = "Insufficient funds" if i % 2 == 0 else "Card declined"
        elif roll == 18:
            status = PaymentStatus.PENDING
            completed_at = None
            failed_at = None
            failure_reason = None
        else:
            status = PaymentStatus.REFUNDED
            created = booking.created_at
            if created and created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            completed_at = created + timedelta(minutes=1) if created else now
            failed_at = None
            failure_reason = None

        payment = Payment(
            gym_id=booking.gym_id,
            consumer_id=booking.consumer_id,
            amount_cents=booking.price_paid_cents,
            currency="ZAR",
            payment_type=PaymentType.CLASS_BOOKING,
            status=status,
            provider=provider,
            provider_reference=f"OZW-{uuid.uuid4().hex[:12].upper()}"
            if provider == PaymentProviderName.OZOW
            else f"PF-{uuid.uuid4().hex[:10].upper()}",
            description="Class booking payment",
            related_entity_id=booking.id,
            completed_at=completed_at,
            failed_at=failed_at,
            failure_reason=failure_reason,
            refunded_at=completed_at + timedelta(days=2)
            if status == PaymentStatus.REFUNDED
            else None,
            retry_count=1 if status == PaymentStatus.FAILED else 0,
        )
        session.add(payment)
        count += 1

    session.commit()
    return count
