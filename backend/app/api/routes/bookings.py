from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import col, select

from app.api.deps import CurrentConsumer, CurrentStaff, SessionDep
from app.core import security
from app.core.config import settings
from app.models import (
    Booking,
    BookingSource,
    BookingStatus,
    BookingType,
    CheckInRecord,
    CheckInSource,
    ClassSession,
    Consumer,
    DigitalWaiverAcceptance,
    Gym,
    GymMembership,
    GymMembershipStatus,
    WaitlistEntry,
    WaitlistStatus,
)
from app.models.payment import Payment, PaymentStatus, PaymentType
from app.services.payments.providers import (
    get_default_payment_provider,
    get_payment_provider,
)

router = APIRouter(prefix="/gyms", tags=["bookings"])
WAITLIST_OFFER_MINUTES = 30
QR_TOKEN_MINUTES = 5


class MembershipBookingRequest(BaseModel):
    gym_id: UUID
    session_id: UUID
    source: BookingSource = BookingSource.DIRECT


class PayPerClassBookingRequest(BaseModel):
    gym_id: UUID
    session_id: UUID
    amount_cents: int
    source: BookingSource = BookingSource.DIRECT
    return_url: str
    cancel_url: str


class PayPerClassResponse(BaseModel):
    booking_id: UUID
    payment_id: UUID
    redirect_url: str
    status: BookingStatus


class CancelBookingResponse(BaseModel):
    booking_id: UUID
    status: BookingStatus
    refunded: bool


class WaitlistJoinRequest(BaseModel):
    gym_id: UUID
    session_id: UUID


class WaitlistOfferResponse(BaseModel):
    waitlist_entry_id: UUID
    expires_at: datetime


class QrCodeResponse(BaseModel):
    token: str
    expires_at: datetime
    consumer_name: str
    todays_booking_ids: list[UUID]


class ConsumerBookingItem(BaseModel):
    id: UUID
    status: BookingStatus
    booking_type: BookingType
    class_name: str
    gym_name: str
    start_time: datetime
    end_time: datetime
    created_at: datetime
    price_paid_cents: int | None
    cancellation_refunded: bool


class ConsumerBookingsResponse(BaseModel):
    items: list[ConsumerBookingItem]
    total: int


class ScanQrRequest(BaseModel):
    token: str


class ManualCheckInRequest(BaseModel):
    consumer_id: UUID
    booking_id: UUID | None = None


class OfflineCheckInRequest(BaseModel):
    consumer_id: UUID
    booking_id: UUID | None = None
    offline_recorded_at: datetime


class OfflineSyncRequest(BaseModel):
    records: list[OfflineCheckInRequest]


class SearchResult(BaseModel):
    consumer_id: UUID
    first_name: str
    last_name: str
    phone: str | None


def _get_session_or_404(
    session: SessionDep, session_id: UUID, *, lock: bool = False
) -> ClassSession:
    """Load a class session, optionally taking a row lock on it.

    Pass ``lock=True`` for anything that reads ``spots_booked`` and then writes
    it. ``SELECT ... FOR UPDATE`` serialises the check and the increment against
    concurrent requests for the same class; without it two callers could both
    see the last spot free and both take it.

    ``populate_existing`` is not optional here. Without it SQLAlchemy returns
    whatever instance the identity map already holds without refreshing its
    columns, so we would acquire the lock and then decide on a stale
    ``spots_booked`` — the lock would be real and useless.
    """
    if lock:
        class_session = session.exec(
            select(ClassSession)
            .where(ClassSession.id == session_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        ).first()
    else:
        class_session = session.get(ClassSession, session_id)
    if not class_session or not class_session.is_active:
        raise HTTPException(status_code=404, detail="Class session not found")
    return class_session


def _active_booking(
    session: SessionDep, session_id: UUID, consumer_id: UUID
) -> Booking | None:
    """The consumer's existing non-cancelled booking for this class, if any.

    Mirrors the partial unique index ``uq_booking_session_consumer_active`` so
    the API can answer 409 rather than let the database raise. Callers must
    already hold the class session's row lock for this to be race-free.
    """
    return session.exec(
        select(Booking).where(
            Booking.session_id == session_id,
            Booking.consumer_id == consumer_id,
            col(Booking.status) != BookingStatus.CANCELLED,
        )
    ).first()


def _class_is_full(class_session: ClassSession) -> bool:
    """capacity == 0 means unlimited throughout this codebase."""
    return bool(class_session.capacity) and (
        class_session.spots_booked >= class_session.capacity
    )


def _commit_booking(session: SessionDep) -> None:
    """Commit, translating the booking invariants' database errors into 409s.

    Both invariants are checked in Python under the class session's row lock, so
    getting here means something outside this path wrote. The constraints are
    still the last word — this only keeps the API from answering 500 when they
    speak.
    """
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        message = str(exc.orig)
        if "uq_booking_session_consumer_active" in message:
            raise HTTPException(
                status_code=409, detail="You already have a booking for this class"
            ) from exc
        if "ck_class_session_spots_within_capacity" in message:
            raise HTTPException(status_code=409, detail="Class is full") from exc
        raise


def _is_membership_valid(
    session: SessionDep, consumer_id: UUID, gym_id: UUID
) -> tuple[bool, str | None, GymMembership | None]:
    membership = session.exec(
        select(GymMembership).where(
            GymMembership.consumer_id == consumer_id,
            GymMembership.gym_id == gym_id,
            col(GymMembership.is_active).is_(True),
        )
    ).first()
    if not membership or membership.status != GymMembershipStatus.ACTIVE:
        return False, "Membership is inactive or missing", None

    if membership.ended_at and membership.ended_at <= datetime.now(timezone.utc):
        return False, "Membership has expired", membership

    waiver = session.exec(
        select(DigitalWaiverAcceptance).where(
            DigitalWaiverAcceptance.gym_membership_id == membership.id,
            DigitalWaiverAcceptance.consumer_id == consumer_id,
            DigitalWaiverAcceptance.gym_id == gym_id,
        )
    ).first()
    if not waiver:
        return False, "Waiver acceptance required", membership

    return True, None, membership


def _process_waitlist_offer(
    session: SessionDep, gym_id: UUID, session_id: UUID
) -> None:
    entry = session.exec(
        select(WaitlistEntry)
        .where(
            WaitlistEntry.gym_id == gym_id,
            WaitlistEntry.session_id == session_id,
            WaitlistEntry.status == WaitlistStatus.WAITLISTED,
        )
        .order_by(col(WaitlistEntry.position))
    ).first()
    if not entry:
        return
    entry.offer(datetime.now(timezone.utc) + timedelta(minutes=WAITLIST_OFFER_MINUTES))
    session.add(entry)


def _gym_cancellation_window_hours(gym: Gym) -> int:
    raw_value = (gym.settings or {}).get("cancellation_window_hours", 24)
    if isinstance(raw_value, str | int):
        try:
            parsed = int(raw_value)
        except ValueError:
            parsed = 24
    else:
        parsed = 24
    return max(0, min(168, parsed))


@router.post("/consumer/bookings/membership", response_model=Booking)
def book_with_membership(
    payload: MembershipBookingRequest,
    current_consumer: CurrentConsumer,
    session: SessionDep,
) -> Booking:
    # Lock the class session row: everything from here to the commit is the
    # check-then-increment that used to race.
    class_session = _get_session_or_404(session, payload.session_id, lock=True)
    if class_session.gym_id != payload.gym_id:
        raise HTTPException(status_code=400, detail="Session does not belong to gym")

    valid, message, membership = _is_membership_valid(
        session, current_consumer.id, payload.gym_id
    )
    if not valid or membership is None:
        raise HTTPException(status_code=400, detail=message)

    if _active_booking(session, payload.session_id, current_consumer.id):
        raise HTTPException(
            status_code=409, detail="You already have a booking for this class"
        )

    if _class_is_full(class_session):
        raise HTTPException(status_code=409, detail="Class is full")

    booking = Booking(
        gym_id=payload.gym_id,
        consumer_id=current_consumer.id,
        session_id=payload.session_id,
        gym_membership_id=membership.id,
        booking_type=BookingType.MEMBERSHIP_BENEFIT,
        source=payload.source,
        status=BookingStatus.BOOKED,
    )
    class_session.spots_booked += 1
    session.add(booking)
    session.add(class_session)
    _commit_booking(session)
    session.refresh(booking)
    return booking


@router.post(
    "/consumer/bookings/pay_per_class",
    response_model=PayPerClassResponse,
    status_code=201,
)
def book_pay_per_class(
    payload: PayPerClassBookingRequest,
    current_consumer: CurrentConsumer,
    session: SessionDep,
) -> PayPerClassResponse:
    # Lock the class session row for the whole check-then-increment below.
    class_session = _get_session_or_404(session, payload.session_id, lock=True)
    if class_session.gym_id != payload.gym_id:
        raise HTTPException(status_code=400, detail="Session does not belong to gym")

    # Auto-expire stale PENDING_PAYMENT bookings for this consumer+session (>1 hour)
    stale_cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
    stale_bookings = list(
        session.exec(
            select(Booking).where(
                Booking.consumer_id == current_consumer.id,
                Booking.session_id == payload.session_id,
                Booking.status == BookingStatus.PENDING_PAYMENT,
                Booking.created_at < stale_cutoff,
            )
        ).all()
    )
    for stale in stale_bookings:
        stale.mark_cancelled()
        if class_session.spots_booked > 0:
            class_session.spots_booked -= 1
        session.add(stale)
    if stale_bookings:
        session.add(class_session)
        session.flush()

    # After the stale sweep, so a lapsed pending booking does not block a retry.
    if _active_booking(session, payload.session_id, current_consumer.id):
        raise HTTPException(
            status_code=409, detail="You already have a booking for this class"
        )

    if _class_is_full(class_session):
        raise HTTPException(status_code=409, detail="Class is full")
    if payload.amount_cents != class_session.price_cents:
        raise HTTPException(
            status_code=400, detail="Payment amount does not match class price"
        )

    booking = Booking(
        gym_id=payload.gym_id,
        consumer_id=current_consumer.id,
        session_id=payload.session_id,
        booking_type=BookingType.PAY_PER_CLASS,
        price_paid_cents=payload.amount_cents,
        source=payload.source,
        status=BookingStatus.PENDING_PAYMENT,
    )
    # Hold the spot while payment processes; released on failure via webhook
    class_session.spots_booked += 1
    session.add(booking)
    session.add(class_session)
    session.flush()

    provider_name = get_default_payment_provider()
    payment = Payment(
        gym_id=payload.gym_id,
        consumer_id=current_consumer.id,
        amount_cents=payload.amount_cents,
        currency="ZAR",
        payment_type=PaymentType.CLASS_BOOKING,
        status=PaymentStatus.PENDING,
        provider=provider_name,
        description=f"Class: {class_session.title}",
        return_url=payload.return_url,
        cancel_url=payload.cancel_url,
        related_entity_id=booking.id,
        extra_data={"class_name": class_session.title},
    )
    provider = get_payment_provider(provider_name)
    initiation = provider.initiate(payment)
    payment.provider_reference = initiation.provider_reference
    session.add(payment)
    _commit_booking(session)
    session.refresh(booking)

    return PayPerClassResponse(
        booking_id=booking.id,
        payment_id=payment.id,
        redirect_url=initiation.redirect_url,
        status=booking.status,
    )


@router.post(
    "/consumer/bookings/{booking_id}/cancel", response_model=CancelBookingResponse
)
def cancel_booking(
    booking_id: UUID, current_consumer: CurrentConsumer, session: SessionDep
) -> CancelBookingResponse:
    booking = session.get(Booking, booking_id)
    if not booking or booking.consumer_id != current_consumer.id:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Lock: the decrement below is the same read-modify-write as the increment.
    class_session = session.exec(
        select(ClassSession)
        .where(ClassSession.id == booking.session_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    ).first()
    if class_session is None:
        raise HTTPException(status_code=404, detail="Class session not found")

    gym = session.get(Gym, booking.gym_id)
    if gym is None:
        raise HTTPException(status_code=404, detail="Gym not found")

    if booking.status == BookingStatus.CANCELLED:
        return CancelBookingResponse(
            booking_id=booking.id,
            status=booking.status,
            refunded=booking.cancellation_refunded,
        )

    now = datetime.now(timezone.utc)
    window_hours = _gym_cancellation_window_hours(gym)
    start_time = class_session.start_time
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    refundable = now <= (start_time - timedelta(hours=window_hours))

    booking.mark_cancelled()
    booking.cancellation_refunded = refundable
    class_session.spots_booked = max(0, class_session.spots_booked - 1)
    session.add(booking)
    session.add(class_session)
    _process_waitlist_offer(session, booking.gym_id, booking.session_id)
    session.commit()

    return CancelBookingResponse(
        booking_id=booking.id, status=booking.status, refunded=refundable
    )


@router.post("/consumer/waitlist", response_model=WaitlistEntry)
def join_waitlist(
    payload: WaitlistJoinRequest, current_consumer: CurrentConsumer, session: SessionDep
) -> WaitlistEntry:
    class_session = _get_session_or_404(session, payload.session_id)
    if class_session.gym_id != payload.gym_id:
        raise HTTPException(status_code=400, detail="Session does not belong to gym")
    if not class_session.waitlist_enabled:
        raise HTTPException(status_code=400, detail="Waitlist is disabled")
    if (
        class_session.capacity == 0
        or class_session.spots_booked < class_session.capacity
    ):
        raise HTTPException(
            status_code=400, detail="Class has open spots; book directly"
        )

    existing = session.exec(
        select(WaitlistEntry).where(
            WaitlistEntry.gym_id == payload.gym_id,
            WaitlistEntry.session_id == payload.session_id,
            WaitlistEntry.consumer_id == current_consumer.id,
            col(WaitlistEntry.status).in_(
                [WaitlistStatus.WAITLISTED, WaitlistStatus.OFFERED]
            ),
        )
    ).first()
    if existing:
        return existing

    queue = session.exec(
        select(WaitlistEntry).where(
            WaitlistEntry.gym_id == payload.gym_id,
            WaitlistEntry.session_id == payload.session_id,
        )
    ).all()
    entry = WaitlistEntry(
        gym_id=payload.gym_id,
        session_id=payload.session_id,
        consumer_id=current_consumer.id,
        position=len(queue) + 1,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.post("/consumer/waitlist/{waitlist_entry_id}/accept", response_model=Booking)
def accept_waitlist_offer(
    waitlist_entry_id: UUID, current_consumer: CurrentConsumer, session: SessionDep
) -> Booking:
    entry = session.get(WaitlistEntry, waitlist_entry_id)
    if not entry or entry.consumer_id != current_consumer.id:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    if entry.status != WaitlistStatus.OFFERED:
        raise HTTPException(status_code=400, detail="Waitlist offer is not active")
    if not entry.expires_at or entry.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Waitlist offer expired")

    # Lock: accepting an offer increments spots_booked like any other booking.
    # This path had no capacity check at all, so it could oversell a class even
    # single-threaded; the check is now here as well as in the database.
    class_session = session.exec(
        select(ClassSession)
        .where(ClassSession.id == entry.session_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    ).first()
    if class_session is None:
        raise HTTPException(status_code=404, detail="Class session not found")

    if _active_booking(session, entry.session_id, entry.consumer_id):
        raise HTTPException(
            status_code=409, detail="You already have a booking for this class"
        )
    if _class_is_full(class_session):
        raise HTTPException(
            status_code=409, detail="The spot was taken before the offer was accepted"
        )

    booking = Booking(
        gym_id=entry.gym_id,
        consumer_id=entry.consumer_id,
        session_id=entry.session_id,
        booking_type=BookingType.MEMBERSHIP_BENEFIT,
        source=BookingSource.DIRECT,
    )
    entry.accept()
    class_session.spots_booked += 1
    session.add(booking)
    session.add(entry)
    session.add(class_session)
    _commit_booking(session)
    session.refresh(booking)
    return booking


@router.post("/system/waitlist/expire_offers")
def expire_waitlist_offers(session: SessionDep) -> dict[str, int]:
    now = datetime.now(timezone.utc)
    expired = session.exec(
        select(WaitlistEntry).where(
            WaitlistEntry.status == WaitlistStatus.OFFERED,
            col(WaitlistEntry.expires_at).is_not(None),
            col(WaitlistEntry.expires_at) < now,
        )
    ).all()
    count = 0
    for entry in expired:
        entry.expire()
        session.add(entry)
        _process_waitlist_offer(session, entry.gym_id, entry.session_id)
        count += 1
    session.commit()
    return {"expired": count}


@router.get("/consumer/bookings", response_model=ConsumerBookingsResponse)
def list_consumer_bookings(
    current_consumer: CurrentConsumer,
    session: SessionDep,
    status: BookingStatus | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ConsumerBookingsResponse:
    """List the authenticated consumer's bookings with class and gym details."""
    query = (
        select(Booking, ClassSession, Gym)
        .join(ClassSession, col(ClassSession.id) == col(Booking.session_id))
        .join(Gym, col(Gym.id) == col(Booking.gym_id))
        .where(Booking.consumer_id == current_consumer.id)
    )
    if status is not None:
        query = query.where(Booking.status == status)

    count_query = select(Booking.id).where(Booking.consumer_id == current_consumer.id)
    if status is not None:
        count_query = count_query.where(Booking.status == status)
    total = len(session.exec(count_query).all())

    rows = session.exec(
        query.order_by(col(ClassSession.start_time).desc()).offset(offset).limit(limit)
    ).all()

    items = [
        ConsumerBookingItem(
            id=booking.id,
            status=booking.status,
            booking_type=booking.booking_type,
            class_name=class_session.title,
            gym_name=gym.name,
            start_time=class_session.start_time,
            end_time=class_session.end_time,
            created_at=booking.created_at,
            price_paid_cents=booking.price_paid_cents,
            cancellation_refunded=booking.cancellation_refunded,
        )
        for booking, class_session, gym in rows
    ]

    return ConsumerBookingsResponse(items=items, total=total)


@router.get("/consumer/qr_code", response_model=QrCodeResponse)
def get_consumer_qr(
    current_consumer: CurrentConsumer, session: SessionDep
) -> QrCodeResponse:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=QR_TOKEN_MINUTES)
    token = jwt.encode(
        {
            "sub": str(current_consumer.id),
            "type": "check_in_qr",
            "exp": expires_at,
        },
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )

    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    rows = session.exec(
        select(Booking.id)
        .join(ClassSession, col(ClassSession.id) == col(Booking.session_id))
        .where(
            Booking.consumer_id == current_consumer.id,
            Booking.status == BookingStatus.BOOKED,
            ClassSession.start_time >= today_start,
            ClassSession.start_time < today_end,
        )
    ).all()

    return QrCodeResponse(
        token=token,
        expires_at=expires_at,
        consumer_name=f"{current_consumer.first_name} {current_consumer.last_name}".strip(),
        todays_booking_ids=list(rows),
    )


@router.post("/me/check_ins/scan_qr", response_model=CheckInRecord)
def scan_qr(
    payload: ScanQrRequest, current_staff: CurrentStaff, session: SessionDep
) -> CheckInRecord:
    if current_staff.role not in {"owner", "manager", "front_desk"}:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        decoded = jwt.decode(
            payload.token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=400, detail="Invalid QR token") from e

    if decoded.get("type") != "check_in_qr":
        raise HTTPException(status_code=400, detail="Invalid QR token")

    consumer_id = UUID(decoded["sub"])
    valid, message, _membership = _is_membership_valid(
        session, consumer_id, current_staff.gym_id
    )
    if not valid:
        raise HTTPException(status_code=400, detail=message)

    booking = session.exec(
        select(Booking)
        .where(
            Booking.consumer_id == consumer_id,
            Booking.gym_id == current_staff.gym_id,
            Booking.status == BookingStatus.BOOKED,
        )
        .order_by(col(Booking.created_at).desc())
    ).first()
    if booking:
        booking.mark_checked_in()
        session.add(booking)

    record = CheckInRecord(
        gym_id=current_staff.gym_id,
        consumer_id=consumer_id,
        booking_id=booking.id if booking else None,
        source=CheckInSource.QR,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.get("/me/check_ins/search", response_model=list[SearchResult])
def search_members_for_check_in(
    current_staff: CurrentStaff,
    session: SessionDep,
    q: str = Query(..., min_length=2),
) -> list[SearchResult]:
    if current_staff.role not in {"owner", "manager", "front_desk"}:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    memberships = session.exec(
        select(GymMembership).where(
            GymMembership.gym_id == current_staff.gym_id,
            col(GymMembership.is_active).is_(True),
        )
    ).all()
    consumer_ids = [m.consumer_id for m in memberships]
    if not consumer_ids:
        return []

    q_lower = q.lower()
    consumers = session.exec(
        select(Consumer).where(col(Consumer.id).in_(consumer_ids))
    ).all()
    matches = [
        c
        for c in consumers
        if q_lower in c.first_name.lower()
        or q_lower in c.last_name.lower()
        or (c.phone and q_lower in c.phone.lower())
    ]
    return [
        SearchResult(
            consumer_id=c.id,
            first_name=c.first_name,
            last_name=c.last_name,
            phone=c.phone,
        )
        for c in matches
    ]


@router.post("/me/check_ins/manual", response_model=CheckInRecord)
def manual_check_in(
    payload: ManualCheckInRequest, current_staff: CurrentStaff, session: SessionDep
) -> CheckInRecord:
    if current_staff.role not in {"owner", "manager", "front_desk"}:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    valid, message, _membership = _is_membership_valid(
        session, payload.consumer_id, current_staff.gym_id
    )
    if not valid:
        raise HTTPException(status_code=400, detail=message)

    booking: Booking | None = None
    if payload.booking_id is not None:
        booking = session.get(Booking, payload.booking_id)
        if (
            booking
            and booking.gym_id == current_staff.gym_id
            and booking.status == BookingStatus.BOOKED
        ):
            booking.mark_checked_in()
            session.add(booking)

    record = CheckInRecord(
        gym_id=current_staff.gym_id,
        consumer_id=payload.consumer_id,
        booking_id=booking.id if booking else None,
        source=CheckInSource.MANUAL,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.post("/me/check_ins/offline_sync")
def offline_sync(
    payload: OfflineSyncRequest, current_staff: CurrentStaff, session: SessionDep
) -> dict[str, int]:
    if current_staff.role not in {"owner", "manager", "front_desk"}:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    synced = 0
    for r in payload.records:
        valid, _, _membership = _is_membership_valid(
            session, r.consumer_id, current_staff.gym_id
        )
        if not valid:
            continue

        booking: Booking | None = None
        if r.booking_id:
            booking = session.get(Booking, r.booking_id)
            if (
                booking
                and booking.gym_id == current_staff.gym_id
                and booking.status == BookingStatus.BOOKED
            ):
                booking.mark_checked_in()
                session.add(booking)

        record = CheckInRecord(
            gym_id=current_staff.gym_id,
            consumer_id=r.consumer_id,
            booking_id=booking.id if booking else None,
            source=CheckInSource.OFFLINE_QR,
            offline_recorded_at=r.offline_recorded_at,
            synced_at=datetime.now(timezone.utc),
        )
        session.add(record)
        synced += 1

    session.commit()
    return {"synced": synced}
