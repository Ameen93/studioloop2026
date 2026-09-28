from datetime import date, datetime, time, timedelta, timezone
from hashlib import sha256
from math import asin, cos, radians, sin, sqrt
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlmodel import col, select

from app.api.deps import CurrentConsumer, SessionDep
from app.models import (
    Booking,
    BookingSource,
    BookingStatus,
    BookingType,
    ClassSession,
    ClassSessionStatus,
    Gym,
    MarketplacePlanTier,
    MarketplaceSubscription,
    MarketplaceSubscriptionStatus,
    ReferralInvite,
    Space,
    Staff,
)
from app.models.payment import Payment, PaymentStatus, PaymentType
from app.services.payments.providers import (
    get_default_payment_provider,
    get_payment_provider,
)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    )
    return round(2 * r * asin(sqrt(a)), 2)


class UpcomingGymClass(BaseModel):
    session_id: UUID
    title: str
    start_time: datetime
    price_cents: int
    spots_remaining: int


class GymProfileResponse(BaseModel):
    gym_id: UUID
    slug: str
    name: str
    description: str | None
    tagline: str | None
    logo_url: str | None
    cover_photo_urls: list[str]
    address_line1: str | None
    city: str | None
    province: str | None
    business_hours: dict[str, dict[str, str | bool | None]]
    amenities: list[str]
    distance_km: float | None
    upcoming_marketplace_classes: list[UpcomingGymClass]


class MarketplaceClassItem(BaseModel):
    session_id: UUID
    gym_id: UUID
    gym_name: str
    title: str
    start_time: datetime
    end_time: datetime
    capacity: int
    spots_booked: int
    price_cents: int
    city: str | None
    province: str | None
    space_name: str | None


class MarketplaceClassDetailResponse(BaseModel):
    session_id: UUID
    gym_id: UUID
    gym_name: str
    title: str
    class_type: str
    description: str | None
    duration_minutes: int
    start_time: datetime
    end_time: datetime
    capacity: int
    spots_booked: int
    spots_remaining: int
    waitlist_enabled: bool
    price_cents: int
    booking_action: str
    space_name: str | None
    address_line1: str | None
    city: str | None
    province: str | None
    map_link: str | None
    instructor_name: str | None
    instructor_bio: str | None
    cancellation_policy: str


class SubscribeRequest(BaseModel):
    plan_tier: MarketplacePlanTier
    return_url: str
    cancel_url: str


class MarketplaceSubscribeResponse(BaseModel):
    subscription_id: UUID
    payment_id: UUID
    redirect_url: str
    status: MarketplaceSubscriptionStatus
    plan_tier: MarketplacePlanTier
    classes_total: int


class MarketplaceSubscriptionResponse(BaseModel):
    subscription_id: UUID
    plan_tier: MarketplacePlanTier
    classes_total: int
    classes_remaining: int
    reset_at: datetime
    status: MarketplaceSubscriptionStatus
    manage_options: list[str]


class ManageSubscriptionRequest(BaseModel):
    action: str = Field(pattern="^(upgrade|downgrade|pause|cancel)$")
    target_tier: MarketplacePlanTier | None = None


class MarketplaceSubscriptionBookingRequest(BaseModel):
    session_id: UUID


class ShareClassResponse(BaseModel):
    class_session_id: UUID
    channels: list[str]
    share_text: str
    share_link: str


class ReferralLinkResponse(BaseModel):
    referral_code: str
    referral_link: str
    channels: list[str]


class ReferralTrackSignupRequest(BaseModel):
    referral_code: str
    email: str


_PLAN_ALLOCATIONS: dict[MarketplacePlanTier, int] = {
    MarketplacePlanTier.EIGHT: 8,
    MarketplacePlanTier.TWELVE: 12,
    MarketplacePlanTier.UNLIMITED: 999_999,
}

_PLAN_PRICES: dict[MarketplacePlanTier, int] = {
    MarketplacePlanTier.EIGHT: 79900,  # R799/month
    MarketplacePlanTier.TWELVE: 99900,  # R999/month
    MarketplacePlanTier.UNLIMITED: 149900,  # R1,499/month
}


def _get_latest_subscription(
    session: SessionDep, consumer_id: UUID
) -> MarketplaceSubscription | None:
    return session.exec(
        select(MarketplaceSubscription)
        .where(MarketplaceSubscription.consumer_id == consumer_id)
        .order_by(col(MarketplaceSubscription.created_at).desc())
    ).first()


def _next_month_reset_at(now: datetime) -> datetime:
    if now.month == 12:
        return now.replace(
            year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
    return now.replace(
        month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0
    )


@router.get("/classes", response_model=list[MarketplaceClassItem])
def browse_marketplace_classes(
    _current_consumer: CurrentConsumer,
    session: SessionDep,
    class_type: str | None = Query(default=None, min_length=1, max_length=80),
    city: str | None = Query(default=None, min_length=1, max_length=100),
    province: str | None = Query(default=None, min_length=1, max_length=100),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    start_time_from: time | None = Query(default=None),
    start_time_to: time | None = Query(default=None),
    min_price_cents: int | None = Query(default=None, ge=0),
    max_price_cents: int | None = Query(default=None, ge=0),
    only_available: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[MarketplaceClassItem]:
    now = datetime.now(timezone.utc)

    query = (
        select(ClassSession, Gym, Space)
        .join(Gym, col(Gym.id) == col(ClassSession.gym_id))
        .join(Space, col(Space.id) == col(ClassSession.space_id))
        .where(
            col(ClassSession.is_active).is_(True),
            col(Gym.is_active).is_(True),
            col(Gym.is_marketplace_enabled).is_(True),
            col(Space.is_active).is_(True),
            ClassSession.status == ClassSessionStatus.SCHEDULED,
            ClassSession.start_time >= now,
        )
    )
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400, detail="start_date must be on or before end_date"
        )
    if start_time_from and start_time_to and start_time_from > start_time_to:
        raise HTTPException(
            status_code=400, detail="start_time_from must be on or before start_time_to"
        )
    if (
        min_price_cents is not None
        and max_price_cents is not None
        and min_price_cents > max_price_cents
    ):
        raise HTTPException(
            status_code=400, detail="min_price_cents must be <= max_price_cents"
        )

    if class_type:
        class_type_value = (
            class_type.strip()
            .replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )
        query = query.where(
            col(ClassSession.title).ilike(f"%{class_type_value}%", escape="\\")
        )
    if city:
        city_value = city.strip().lower()
        query = query.where(func.lower(Gym.city) == city_value)
    if province:
        province_value = province.strip().lower()
        query = query.where(func.lower(Gym.province) == province_value)
    if start_date:
        query = query.where(
            ClassSession.start_time
            >= datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        )
    if end_date:
        query = query.where(
            ClassSession.start_time
            <= datetime.combine(end_date, time.max, tzinfo=timezone.utc)
        )
    if min_price_cents is not None:
        query = query.where(ClassSession.price_cents >= min_price_cents)
    if max_price_cents is not None:
        query = query.where(ClassSession.price_cents <= max_price_cents)

    rows = session.exec(query.order_by(col(ClassSession.start_time))).all()

    filtered_rows: list[tuple[ClassSession, Gym, Space]] = []
    for class_session, gym, space in rows:
        session_time = class_session.start_time.time()
        if start_time_from and session_time < start_time_from:
            continue
        if start_time_to and session_time > start_time_to:
            continue
        if (
            only_available
            and class_session.capacity
            and class_session.spots_booked >= class_session.capacity
        ):
            continue
        filtered_rows.append((class_session, gym, space))
    rows = filtered_rows

    rows = rows[:limit]

    return [
        MarketplaceClassItem(
            session_id=class_session.id,
            gym_id=gym.id,
            gym_name=gym.name,
            title=class_session.title,
            start_time=class_session.start_time,
            end_time=class_session.end_time,
            capacity=class_session.capacity,
            spots_booked=class_session.spots_booked,
            price_cents=class_session.price_cents,
            city=gym.city,
            province=gym.province,
            space_name=space.name,
        )
        for class_session, gym, space in rows
    ]


@router.get("/gyms/{gym_id}", response_model=GymProfileResponse)
def view_marketplace_gym_profile(
    gym_id: UUID,
    _current_consumer: CurrentConsumer,
    session: SessionDep,
    current_latitude: float | None = Query(default=None),
    current_longitude: float | None = Query(default=None),
) -> GymProfileResponse:
    gym = session.get(Gym, gym_id)
    if not gym or not gym.is_active or not gym.is_marketplace_enabled:
        raise HTTPException(status_code=404, detail="Gym profile not found")

    upcoming_rows = session.exec(
        select(ClassSession)
        .where(
            ClassSession.gym_id == gym.id,
            col(ClassSession.is_active).is_(True),
            ClassSession.status == ClassSessionStatus.SCHEDULED,
            ClassSession.start_time >= datetime.now(timezone.utc),
        )
        .order_by(col(ClassSession.start_time))
        .limit(10)
    ).all()

    distance_km: float | None = None
    if (
        current_latitude is not None
        and current_longitude is not None
        and gym.latitude is not None
        and gym.longitude is not None
    ):
        distance_km = _distance_km(
            current_latitude, current_longitude, gym.latitude, gym.longitude
        )

    amenities: list[str] = []
    raw_amenities: object = (gym.settings or {}).get("amenities", [])
    if isinstance(raw_amenities, list):
        amenities = [value for value in raw_amenities if isinstance(value, str)]

    return GymProfileResponse(
        gym_id=gym.id,
        slug=gym.slug,
        name=gym.name,
        description=gym.description,
        tagline=gym.tagline,
        logo_url=gym.logo_url,
        cover_photo_urls=gym.cover_photo_urls,
        address_line1=gym.address_line1,
        city=gym.city,
        province=gym.province,
        business_hours=gym.business_hours,
        amenities=amenities,
        distance_km=distance_km,
        upcoming_marketplace_classes=[
            UpcomingGymClass(
                session_id=row.id,
                title=row.title,
                start_time=row.start_time,
                price_cents=row.price_cents,
                spots_remaining=max(0, row.capacity - row.spots_booked),
            )
            for row in upcoming_rows
        ],
    )


@router.get("/classes/{session_id}", response_model=MarketplaceClassDetailResponse)
def view_marketplace_class_details(
    session_id: UUID,
    _current_consumer: CurrentConsumer,
    session: SessionDep,
) -> MarketplaceClassDetailResponse:
    row = session.exec(
        select(ClassSession, Gym, Space, Staff)
        .join(Gym, col(Gym.id) == col(ClassSession.gym_id))
        .join(Space, col(Space.id) == col(ClassSession.space_id))
        .join(
            Staff, col(Staff.id) == col(ClassSession.instructor_staff_id), isouter=True
        )
        .where(
            ClassSession.id == session_id,
            col(ClassSession.is_active).is_(True),
            ClassSession.status == ClassSessionStatus.SCHEDULED,
            col(Gym.is_active).is_(True),
            col(Gym.is_marketplace_enabled).is_(True),
            col(Space.is_active).is_(True),
        )
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Class details not found")

    class_session, gym, space, instructor = row
    remaining = max(0, class_session.capacity - class_session.spots_booked)
    action = "book" if remaining > 0 else "join_waitlist"
    duration = max(
        1,
        int((class_session.end_time - class_session.start_time).total_seconds() // 60),
    )
    policy_value = (gym.settings or {}).get(
        "cancellation_policy", "Cancel before class starts to avoid penalties."
    )
    cancellation_policy = (
        policy_value
        if isinstance(policy_value, str)
        else "Cancel before class starts to avoid penalties."
    )

    return MarketplaceClassDetailResponse(
        session_id=class_session.id,
        gym_id=class_session.gym_id,
        gym_name=gym.name,
        title=class_session.title,
        class_type=class_session.title.split(" ")[0].lower(),
        description=None,
        duration_minutes=duration,
        start_time=class_session.start_time,
        end_time=class_session.end_time,
        capacity=class_session.capacity,
        spots_booked=class_session.spots_booked,
        spots_remaining=remaining,
        waitlist_enabled=class_session.waitlist_enabled,
        price_cents=class_session.price_cents,
        booking_action=action,
        space_name=space.name,
        address_line1=gym.address_line1,
        city=gym.city,
        province=gym.province,
        map_link=f"https://maps.google.com/?q={gym.latitude},{gym.longitude}"
        if gym.latitude and gym.longitude
        else None,
        instructor_name=f"{instructor.first_name} {instructor.last_name}"
        if instructor
        else None,
        instructor_bio=None,
        cancellation_policy=cancellation_policy,
    )


@router.post(
    "/subscriptions",
    response_model=MarketplaceSubscribeResponse,
    status_code=201,
)
def subscribe_to_marketplace_plan(
    payload: SubscribeRequest,
    current_consumer: CurrentConsumer,
    session: SessionDep,
) -> MarketplaceSubscribeResponse:
    allocation = _PLAN_ALLOCATIONS[payload.plan_tier]
    existing = _get_latest_subscription(session, current_consumer.id)
    if existing and existing.status in (
        MarketplaceSubscriptionStatus.ACTIVE,
        MarketplaceSubscriptionStatus.PENDING_PAYMENT,
    ):
        # Auto-expire stale PENDING_PAYMENT subscriptions (>1 hour old)
        stale_cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
        if (
            existing.status == MarketplaceSubscriptionStatus.PENDING_PAYMENT
            and existing.created_at < stale_cutoff
        ):
            existing.status = MarketplaceSubscriptionStatus.CANCELLED
            existing.cancelled_at = datetime.now(timezone.utc)
            session.add(existing)
            session.flush()
        else:
            raise HTTPException(
                status_code=400,
                detail="Active or pending marketplace subscription already exists",
            )

    now = datetime.now(timezone.utc)
    subscription = MarketplaceSubscription(
        consumer_id=current_consumer.id,
        plan_tier=payload.plan_tier,
        classes_total=allocation,
        classes_remaining=allocation,
        reset_at=_next_month_reset_at(now),
        status=MarketplaceSubscriptionStatus.PENDING_PAYMENT,
    )
    session.add(subscription)
    session.flush()

    amount_cents = _PLAN_PRICES[payload.plan_tier]
    provider_name = get_default_payment_provider()
    payment = Payment(
        gym_id=None,  # Platform-level payment, no associated gym
        consumer_id=current_consumer.id,
        amount_cents=amount_cents,
        currency="ZAR",
        payment_type=PaymentType.MARKETPLACE_SUBSCRIPTION,
        status=PaymentStatus.PENDING,
        provider=provider_name,
        description=f"Marketplace {payload.plan_tier.value} plan",
        return_url=payload.return_url,
        cancel_url=payload.cancel_url,
        related_entity_id=subscription.id,
    )
    provider = get_payment_provider(provider_name)
    initiation = provider.initiate(payment)
    payment.provider_reference = initiation.provider_reference
    session.add(payment)
    session.commit()
    session.refresh(subscription)

    return MarketplaceSubscribeResponse(
        subscription_id=subscription.id,
        payment_id=payment.id,
        redirect_url=initiation.redirect_url,
        status=subscription.status,
        plan_tier=subscription.plan_tier,
        classes_total=subscription.classes_total,
    )


@router.post("/bookings/subscription", response_model=Booking)
def book_marketplace_class_with_subscription(
    payload: MarketplaceSubscriptionBookingRequest,
    current_consumer: CurrentConsumer,
    session: SessionDep,
) -> Booking:
    class_session = session.get(ClassSession, payload.session_id)
    if (
        not class_session
        or not class_session.is_active
        or class_session.status != ClassSessionStatus.SCHEDULED
    ):
        raise HTTPException(status_code=404, detail="Class session not found")

    gym = session.get(Gym, class_session.gym_id)
    if not gym or not gym.is_active or not gym.is_marketplace_enabled:
        raise HTTPException(status_code=400, detail="Class is not marketplace eligible")

    existing_booking = session.exec(
        select(Booking).where(
            Booking.consumer_id == current_consumer.id,
            Booking.session_id == class_session.id,
            Booking.status == BookingStatus.BOOKED,
        )
    ).first()
    if existing_booking:
        raise HTTPException(status_code=409, detail="Class already booked")

    if class_session.capacity and class_session.spots_booked >= class_session.capacity:
        raise HTTPException(status_code=409, detail="Class is full")

    subscription = _get_latest_subscription(session, current_consumer.id)
    if not subscription or subscription.status != MarketplaceSubscriptionStatus.ACTIVE:
        raise HTTPException(
            status_code=400, detail="Active marketplace subscription required"
        )
    if subscription.classes_remaining <= 0:
        raise HTTPException(status_code=400, detail="No marketplace credits remaining")

    booking = Booking(
        gym_id=class_session.gym_id,
        consumer_id=current_consumer.id,
        session_id=class_session.id,
        booking_type=BookingType.MEMBERSHIP_BENEFIT,
        source=BookingSource.MARKETPLACE,
        status=BookingStatus.BOOKED,
    )
    subscription.classes_remaining -= 1
    class_session.spots_booked += 1
    session.add(booking)
    session.add(subscription)
    session.add(class_session)
    session.commit()
    session.refresh(booking)
    return booking


@router.get("/subscriptions/me", response_model=MarketplaceSubscriptionResponse)
def view_marketplace_subscription_status(
    current_consumer: CurrentConsumer,
    session: SessionDep,
) -> MarketplaceSubscriptionResponse:
    subscription = _get_latest_subscription(session, current_consumer.id)
    if not subscription:
        raise HTTPException(
            status_code=404, detail="Marketplace subscription not found"
        )

    return MarketplaceSubscriptionResponse(
        subscription_id=subscription.id,
        plan_tier=subscription.plan_tier,
        classes_total=subscription.classes_total,
        classes_remaining=subscription.classes_remaining,
        reset_at=subscription.reset_at,
        status=subscription.status,
        manage_options=["upgrade", "downgrade", "pause", "cancel"],
    )


@router.post("/subscriptions/me/manage", response_model=MarketplaceSubscriptionResponse)
def manage_marketplace_subscription(
    payload: ManageSubscriptionRequest,
    current_consumer: CurrentConsumer,
    session: SessionDep,
) -> MarketplaceSubscriptionResponse:
    subscription = _get_latest_subscription(session, current_consumer.id)
    if not subscription:
        raise HTTPException(
            status_code=404, detail="Marketplace subscription not found"
        )

    if subscription.status == MarketplaceSubscriptionStatus.CANCELLED:
        raise HTTPException(
            status_code=400, detail="Cancelled subscriptions cannot be changed"
        )

    if payload.action in {"upgrade", "downgrade"} and payload.target_tier is None:
        raise HTTPException(
            status_code=400, detail="target_tier is required for tier changes"
        )

    if payload.action == "upgrade":
        target_tier = payload.target_tier
        if target_tier is None:
            raise HTTPException(
                status_code=400, detail="target_tier is required for tier changes"
            )
        previous_total = max(1, subscription.classes_total)
        previous_remaining = subscription.classes_remaining
        new_total = _PLAN_ALLOCATIONS[target_tier]
        consumed = max(0, previous_total - previous_remaining)
        subscription.plan_tier = target_tier
        subscription.classes_total = new_total
        subscription.classes_remaining = max(0, new_total - consumed)
        subscription.status = MarketplaceSubscriptionStatus.ACTIVE
    elif payload.action == "downgrade":
        target_tier = payload.target_tier
        if target_tier is None:
            raise HTTPException(
                status_code=400, detail="target_tier is required for tier changes"
            )
        subscription.downgrade_to_tier = target_tier
    elif payload.action == "pause":
        subscription.status = MarketplaceSubscriptionStatus.PAUSED
        subscription.paused_at = datetime.now(timezone.utc)
    elif payload.action == "cancel":
        subscription.status = MarketplaceSubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.now(timezone.utc)

    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    return MarketplaceSubscriptionResponse(
        subscription_id=subscription.id,
        plan_tier=subscription.plan_tier,
        classes_total=subscription.classes_total,
        classes_remaining=subscription.classes_remaining,
        reset_at=subscription.reset_at,
        status=subscription.status,
        manage_options=["upgrade", "downgrade", "pause", "cancel"],
    )


@router.get("/classes/{session_id}/share", response_model=ShareClassResponse)
def share_class_details(
    session_id: UUID,
    _current_consumer: CurrentConsumer,
    session: SessionDep,
) -> ShareClassResponse:
    row = session.exec(
        select(ClassSession, Gym)
        .join(Gym, col(Gym.id) == col(ClassSession.gym_id))
        .where(
            ClassSession.id == session_id,
            col(ClassSession.is_active).is_(True),
            col(Gym.is_active).is_(True),
            col(Gym.is_marketplace_enabled).is_(True),
        )
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Class details not found")

    class_session, gym = row
    share_link = f"https://app.studioloop.test/classes/{class_session.id}"
    share_text = (
        f"Join me for {class_session.title} at {gym.name} on "
        f"{class_session.start_time.strftime('%Y-%m-%d %H:%M')}! Book here: {share_link}"
    )
    return ShareClassResponse(
        class_session_id=class_session.id,
        channels=["whatsapp", "sms", "email", "copy_link"],
        share_text=share_text,
        share_link=share_link,
    )


@router.get("/referrals/me", response_model=ReferralLinkResponse)
def get_referral_link(
    current_consumer: CurrentConsumer, session: SessionDep
) -> ReferralLinkResponse:
    referral_code = f"sl-{sha256(f'{current_consumer.id}'.encode()).hexdigest()[:12]}"
    existing = session.exec(
        select(ReferralInvite).where(
            ReferralInvite.referrer_consumer_id == current_consumer.id,
            ReferralInvite.referral_code == referral_code,
            ReferralInvite.channel == "link_generated",
        )
    ).first()
    if not existing:
        session.add(
            ReferralInvite(
                referrer_consumer_id=current_consumer.id,
                referral_code=referral_code,
                channel="link_generated",
            )
        )
        session.commit()

    return ReferralLinkResponse(
        referral_code=referral_code,
        referral_link=f"https://app.studioloop.test/signup?ref={referral_code}",
        channels=["whatsapp", "sms", "email", "copy_link"],
    )


@router.post("/referrals/track-signup")
def track_referral_signup(
    payload: ReferralTrackSignupRequest,
    _current_consumer: CurrentConsumer,
    session: SessionDep,
) -> dict[str, str]:
    owner = session.exec(
        select(ReferralInvite)
        .where(ReferralInvite.referral_code == payload.referral_code)
        .order_by(col(ReferralInvite.created_at).asc())
    ).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Referral code not found")

    invite = ReferralInvite(
        referrer_consumer_id=owner.referrer_consumer_id,
        referral_code=payload.referral_code,
        channel="signup",
        referred_email_hash=sha256(payload.email.strip().lower().encode()).hexdigest(),
        signed_up_at=datetime.now(timezone.utc),
    )
    session.add(invite)
    session.commit()
    return {"status": "tracked"}
