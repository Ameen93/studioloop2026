from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, Request
from pydantic import BaseModel, Field, HttpUrl
from sqlmodel import select

from app.api.deps import CurrentConsumer, CurrentStaff, SessionDep, StaffGymDep
from app.core.config import settings
from app.core.rate_limit import RATE_PAYMENT, RATE_WEBHOOK, limiter
from app.models import (
    Booking,
    BookingStatus,
    ClassSession,
    Consumer,
    GymMembership,
    GymMembershipStatus,
    MarketplaceSubscription,
    MarketplaceSubscriptionStatus,
)
from app.models.payment import (
    Payment,
    PaymentProviderName,
    PaymentReceipt,
    PaymentStatus,
    PaymentType,
    PaymentWebhookEvent,
)
from app.services.payments.providers import (
    UnknownPaymentProviderError,
    build_webhook_signature,
    get_default_payment_provider,
    get_payment_provider,
    stub_webhooks_allowed,
)

router = APIRouter(prefix="/payments", tags=["payments"])


class InitiatePaymentRequest(BaseModel):
    gym_id: UUID
    payment_type: PaymentType
    amount_cents: int = Field(ge=0)
    description: str = Field(min_length=1, max_length=255)
    return_url: HttpUrl
    cancel_url: HttpUrl
    webhook_url: HttpUrl
    provider: PaymentProviderName | None = None
    related_entity_id: UUID | None = None


class InitiatePaymentResponse(BaseModel):
    payment_id: UUID
    status: PaymentStatus
    provider: PaymentProviderName
    provider_reference: str
    redirect_url: str
    expires_in_seconds: int


class PaymentWebhookRequest(BaseModel):
    """Inbound webhook body.

    Deliberately carries no field that can assert its own authenticity: the
    provider's signature over the raw body is the only thing that authenticates
    a webhook. (An earlier `verified: bool` field here was honoured by the
    PayFast stub, which made this route an unauthenticated way to complete any
    payment.)
    """

    event_id: str = Field(min_length=1, max_length=255)
    payment_id: UUID
    status: PaymentStatus
    provider_reference: str | None = Field(default=None, max_length=255)
    event_type: str = Field(default="payment.updated", max_length=64)
    failure_reason: str | None = Field(default=None, max_length=500)


class PaymentItem(BaseModel):
    payment_id: UUID
    member_name: str
    amount_cents: int
    currency: str
    payment_type: PaymentType
    status: PaymentStatus
    created_at: datetime


class GymPaymentsSummary(BaseModel):
    total_received_cents: int
    total_pending_cents: int
    total_failed_cents: int


class GymPaymentsListResponse(BaseModel):
    summary: GymPaymentsSummary
    items: list[PaymentItem]


class GymPaymentDetailResponse(BaseModel):
    payment_id: UUID
    member_name: str
    amount_cents: int
    currency: str
    payment_type: PaymentType
    status: PaymentStatus
    description: str
    provider: PaymentProviderName
    provider_reference: str | None
    failure_reason: str | None
    retry_count: int
    created_at: datetime
    completed_at: datetime | None
    failed_at: datetime | None


class FailedPaymentActionItem(BaseModel):
    payment_id: UUID
    member_name: str
    failure_reason: str | None
    failed_at: datetime | None


class RetryRunResponse(BaseModel):
    processed_payment_ids: list[UUID]


class MarketplacePayoutClassBreakdown(BaseModel):
    class_name: str
    bookings: int
    gross_revenue_cents: int


class MarketplacePayoutReport(BaseModel):
    total_marketplace_bookings: int
    gross_revenue_cents: int
    platform_fee_cents: int
    net_payout_cents: int
    payout_schedule: str
    class_breakdown: list[MarketplacePayoutClassBreakdown]


class CreateSubscriptionRequest(BaseModel):
    gym_id: UUID
    amount_cents: int = Field(ge=0)
    description: str = Field(min_length=1, max_length=255)
    return_url: HttpUrl
    cancel_url: HttpUrl
    webhook_url: HttpUrl
    provider: PaymentProviderName = PaymentProviderName.STITCH
    related_entity_id: UUID | None = None


class CreateSubscriptionResponse(BaseModel):
    payment_id: UUID
    status: PaymentStatus
    provider: PaymentProviderName
    provider_reference: str
    redirect_url: str


class PaymentStatusResponse(BaseModel):
    payment_id: UUID
    status: PaymentStatus
    provider: PaymentProviderName
    provider_reference: str | None
    amount_cents: int
    currency: str
    description: str
    created_at: datetime
    completed_at: datetime | None
    failed_at: datetime | None
    failure_reason: str | None


class ConsumerPaymentHistoryItem(BaseModel):
    payment_id: UUID
    description: str
    amount_cents: int
    currency: str
    payment_type: PaymentType
    status: PaymentStatus
    created_at: datetime
    receipt_id: UUID | None


class ConsumerPaymentHistoryResponse(BaseModel):
    items: list[ConsumerPaymentHistoryItem]


class ReceiptResponse(BaseModel):
    receipt_id: UUID
    payment_id: UUID
    receipt_number: str
    rendered_text: str
    subtotal_cents: int
    vat_amount_cents: int
    total_cents: int
    vat_rate_percent: float


def _retry_offsets() -> list[int]:
    # fixed schedule per story 8.6 requirement
    return [1, 3, 7]


def _build_receipt(payment: Payment, consumer: Consumer) -> PaymentReceipt:
    vat_rate = Decimal("15.0")
    total = Decimal(payment.amount_cents)
    divisor = Decimal("1") + (vat_rate / Decimal("100"))
    subtotal = (total / divisor).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    vat_amount = int(total - subtotal)
    receipt_number = (
        f"RCP-{datetime.now(UTC).strftime('%Y%m%d')}-{str(payment.id)[:8].upper()}"
    )
    rendered = (
        f"StudioLoop Receipt\n"
        f"Date: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        f"Receipt #: {receipt_number}\n"
        f"Payment Ref: {payment.provider_reference or payment.id}\n"
        f"Consumer: {consumer.first_name} {consumer.last_name}\n"
        f"Description: {payment.description}\n"
        f"Payment Method: {payment.provider.value}\n"
        f"Subtotal: {int(subtotal)} {payment.currency}\n"
        f"VAT ({vat_rate}%): {vat_amount} {payment.currency}\n"
        f"Total: {payment.amount_cents} {payment.currency}"
    )
    return PaymentReceipt(
        payment_id=payment.id,
        consumer_id=payment.consumer_id,
        receipt_number=receipt_number,
        vat_rate_percent=float(vat_rate),
        vat_amount_cents=vat_amount,
        subtotal_cents=int(subtotal),
        total_cents=payment.amount_cents,
        rendered_text=rendered,
        emailed_at=datetime.now(UTC),
    )


@router.post("/initiate", response_model=InitiatePaymentResponse)
@limiter.limit(RATE_PAYMENT)
def initiate_payment_flow(
    request: Request,  # noqa: ARG001 — required by slowapi limiter
    payload: InitiatePaymentRequest,
    current_consumer: CurrentConsumer,
    session: SessionDep,
) -> InitiatePaymentResponse:
    provider_name = payload.provider or get_default_payment_provider()
    payment = Payment(
        gym_id=payload.gym_id,
        consumer_id=current_consumer.id,
        amount_cents=payload.amount_cents,
        currency="ZAR",
        payment_type=payload.payment_type,
        status=PaymentStatus.PENDING,
        provider=provider_name,
        description=payload.description,
        return_url=str(payload.return_url),
        cancel_url=str(payload.cancel_url),
        webhook_url=str(payload.webhook_url),
        related_entity_id=payload.related_entity_id,
    )
    provider = get_payment_provider(provider_name)
    initiation = provider.initiate(payment)
    payment.provider_reference = initiation.provider_reference
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return InitiatePaymentResponse(
        payment_id=payment.id,
        status=payment.status,
        provider=payment.provider,
        provider_reference=payment.provider_reference or "",
        redirect_url=initiation.redirect_url,
        expires_in_seconds=900,
    )


@router.post("/subscriptions", response_model=CreateSubscriptionResponse)
def create_subscription(
    payload: CreateSubscriptionRequest,
    current_consumer: CurrentConsumer,
    session: SessionDep,
) -> CreateSubscriptionResponse:
    provider_name = payload.provider
    if provider_name != PaymentProviderName.STITCH:
        raise HTTPException(
            status_code=400, detail="Subscriptions are only supported via Stitch"
        )

    payment = Payment(
        gym_id=payload.gym_id,
        consumer_id=current_consumer.id,
        amount_cents=payload.amount_cents,
        currency="ZAR",
        payment_type=PaymentType.MEMBERSHIP,
        status=PaymentStatus.PENDING,
        provider=provider_name,
        description=payload.description,
        return_url=str(payload.return_url),
        cancel_url=str(payload.cancel_url),
        webhook_url=str(payload.webhook_url),
        related_entity_id=payload.related_entity_id,
    )
    provider = get_payment_provider(provider_name)
    initiation = provider.initiate(payment)
    payment.provider_reference = initiation.provider_reference
    session.add(payment)
    session.commit()
    session.refresh(payment)

    return CreateSubscriptionResponse(
        payment_id=payment.id,
        status=payment.status,
        provider=payment.provider,
        provider_reference=payment.provider_reference or "",
        redirect_url=initiation.redirect_url,
    )


@router.get("/{payment_id:uuid}", response_model=PaymentStatusResponse)
def get_payment_status(
    payment_id: UUID,
    current_consumer: CurrentConsumer,
    session: SessionDep,
) -> PaymentStatusResponse:
    payment = session.get(Payment, payment_id)
    if not payment or payment.consumer_id != current_consumer.id:
        raise HTTPException(status_code=404, detail="Payment not found")

    return PaymentStatusResponse(
        payment_id=payment.id,
        status=payment.status,
        provider=payment.provider,
        provider_reference=payment.provider_reference,
        amount_cents=payment.amount_cents,
        currency=payment.currency,
        description=payment.description,
        created_at=payment.created_at,
        completed_at=payment.completed_at,
        failed_at=payment.failed_at,
        failure_reason=payment.failure_reason,
    )


@router.get("/", response_model=GymPaymentsListResponse)
def list_payments_for_gym(
    current_staff: CurrentStaff,
    session: SessionDep,
    gym_id: UUID = Query(...),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    payment_type: PaymentType | None = Query(default=None),
    status: PaymentStatus | None = Query(default=None),
) -> GymPaymentsListResponse:
    if str(current_staff.gym_id) != str(gym_id):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "Access denied to this gym",
                "details": {},
            },
        )

    query = select(Payment).where(Payment.gym_id == gym_id)
    if start_date:
        query = query.where(Payment.created_at >= start_date)
    if end_date:
        query = query.where(Payment.created_at <= end_date)
    if payment_type:
        query = query.where(Payment.payment_type == payment_type)
    if status:
        query = query.where(Payment.status == status)

    payments = list(session.exec(query).all())
    payments.sort(key=lambda p: p.created_at, reverse=True)
    consumer_ids = list({p.consumer_id for p in payments})
    names: dict[UUID, str] = {}
    for consumer_id in consumer_ids:
        consumer = session.get(Consumer, consumer_id)
        if consumer is not None:
            names[consumer.id] = f"{consumer.first_name} {consumer.last_name}".strip()

    summary = GymPaymentsSummary(
        total_received_cents=sum(
            p.amount_cents for p in payments if p.status == PaymentStatus.COMPLETED
        ),
        total_pending_cents=sum(
            p.amount_cents for p in payments if p.status == PaymentStatus.PENDING
        ),
        total_failed_cents=sum(
            p.amount_cents
            for p in payments
            if p.status in {PaymentStatus.FAILED, PaymentStatus.FAILED_PERMANENT}
        ),
    )
    items = [
        PaymentItem(
            payment_id=p.id,
            member_name=names.get(p.consumer_id, "Unknown Member"),
            amount_cents=p.amount_cents,
            currency=p.currency,
            payment_type=p.payment_type,
            status=p.status,
            created_at=p.created_at,
        )
        for p in payments
    ]
    return GymPaymentsListResponse(summary=summary, items=items)


def _resolve_webhook_provider(provider_path: str | None) -> PaymentProviderName:
    """Decide which provider verifies this webhook.

    The configured provider decides, never the caller. A `{provider}` path
    segment is accepted only as an assertion to cross-check: if it names a
    different provider than PAYMENT_PROVIDER, the request is refused rather than
    silently routed to another verifier. This is the fix for the bypass where the
    path segment selected the verifier, letting a caller pick the stub provider.
    """
    try:
        configured = get_default_payment_provider()
    except UnknownPaymentProviderError as exc:
        # Misconfiguration, not a client error: refuse to process anything.
        raise HTTPException(
            status_code=503, detail="Payment provider is not configured"
        ) from exc

    if provider_path is not None:
        try:
            requested = PaymentProviderName(provider_path.strip().lower())
        except ValueError:
            raise HTTPException(
                status_code=404, detail="Unknown payment provider"
            ) from None
        if requested != configured:
            raise HTTPException(
                status_code=403,
                detail="Webhook provider does not match the configured provider",
            )
    return configured


@router.post("/webhooks/{provider}")
@limiter.limit(RATE_WEBHOOK)
async def process_payment_webhook_for_provider(
    payload: PaymentWebhookRequest,
    session: SessionDep,
    request: Request,
    provider: str,
    x_signature: str | None = Header(default=None, alias="X-Signature"),
    svix_id: str | None = Header(default=None, alias="svix-id"),
    svix_timestamp: str | None = Header(default=None, alias="svix-timestamp"),
    svix_signature: str | None = Header(default=None, alias="svix-signature"),
) -> dict[str, str]:
    return await _handle_payment_webhook(
        payload=payload,
        session=session,
        request=request,
        provider_path=provider,
        x_signature=x_signature,
        svix_id=svix_id,
        svix_timestamp=svix_timestamp,
        svix_signature=svix_signature,
    )


@router.post("/webhook")
@limiter.limit(RATE_WEBHOOK)
async def process_payment_webhook(
    payload: PaymentWebhookRequest,
    session: SessionDep,
    request: Request,
    x_signature: str | None = Header(default=None, alias="X-Signature"),
    svix_id: str | None = Header(default=None, alias="svix-id"),
    svix_timestamp: str | None = Header(default=None, alias="svix-timestamp"),
    svix_signature: str | None = Header(default=None, alias="svix-signature"),
) -> dict[str, str]:
    return await _handle_payment_webhook(
        payload=payload,
        session=session,
        request=request,
        provider_path=None,
        x_signature=x_signature,
        svix_id=svix_id,
        svix_timestamp=svix_timestamp,
        svix_signature=svix_signature,
    )


async def _handle_payment_webhook(
    *,
    payload: PaymentWebhookRequest,
    session: SessionDep,
    request: Request,
    provider_path: str | None,
    x_signature: str | None,
    svix_id: str | None,
    svix_timestamp: str | None,
    svix_signature: str | None,
) -> dict[str, str]:
    provider = _resolve_webhook_provider(provider_path)
    verifier = get_payment_provider(provider)

    # A provider with no signing secret cannot authenticate anything, so it may
    # never be reachable over HTTP outside an opted-in local dev machine. The
    # provider's own verify() refuses too; this is the visible route-level gate.
    # getattr default is False on purpose: a provider object that does not
    # declare the capability is treated as unable to verify, never as able.
    if not getattr(verifier, "can_verify_webhooks", False) and not (
        stub_webhooks_allowed()
    ):
        raise HTTPException(
            status_code=403,
            detail="Configured payment provider cannot verify webhook signatures",
        )

    # Only a previously *verified* delivery counts as processed. Keying
    # idempotency on event_id alone let an unauthenticated caller burn an
    # event_id with a bad signature and permanently suppress the real delivery.
    prior_events = list(
        session.exec(
            select(PaymentWebhookEvent).where(
                PaymentWebhookEvent.event_id == payload.event_id
            )
        ).all()
    )
    if any(prior.signature_valid for prior in prior_events):
        return {"status": "already_processed"}
    rejected_event = prior_events[0] if prior_events else None

    # Authenticate before touching any payment state, and before confirming
    # whether the referenced payment even exists.
    verification_payload = payload.model_dump(mode="json", exclude_none=True)
    if provider == PaymentProviderName.STITCH:
        verification_payload["_svix_id"] = svix_id
        verification_payload["_svix_timestamp"] = svix_timestamp
        verification_payload["_svix_signature"] = svix_signature
        verification_payload["_raw_body"] = (await request.body()).decode()

    verification = verifier.verify(
        verification_payload,
        signature=svix_signature
        if provider == PaymentProviderName.STITCH
        else x_signature,
    )
    if not verification.is_valid:
        if rejected_event is None:
            session.add(
                PaymentWebhookEvent(
                    provider=provider,
                    event_id=payload.event_id,
                    payment_id=None,
                    event_type=payload.event_type,
                    signature_valid=False,
                    payload=payload.model_dump(mode="json", exclude_none=True),
                )
            )
            session.commit()
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    payment = session.get(Payment, payload.payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payload.status == PaymentStatus.COMPLETED:
        payment.mark_completed(provider_reference=payload.provider_reference)

        if payment.related_entity_id:
            if payment.payment_type == PaymentType.MEMBERSHIP:
                membership = session.get(GymMembership, payment.related_entity_id)
                if membership:
                    membership.status = GymMembershipStatus.ACTIVE
                    membership.ended_at = None
                    session.add(membership)
            elif payment.payment_type == PaymentType.CLASS_BOOKING:
                booking = session.get(Booking, payment.related_entity_id)
                if booking:
                    booking.status = BookingStatus.BOOKED
                    session.add(booking)
            elif payment.payment_type == PaymentType.MARKETPLACE_SUBSCRIPTION:
                subscription = session.get(
                    MarketplaceSubscription, payment.related_entity_id
                )
                if subscription:
                    subscription.status = MarketplaceSubscriptionStatus.ACTIVE
                    session.add(subscription)

        receipt = session.exec(
            select(PaymentReceipt).where(PaymentReceipt.payment_id == payment.id)
        ).first()
        if not receipt:
            consumer = session.get(Consumer, payment.consumer_id)
            if consumer:
                session.add(_build_receipt(payment, consumer))

    elif payload.status == PaymentStatus.REFUNDED:
        payment.mark_refunded(provider_reference=payload.provider_reference)
    elif payload.status == PaymentStatus.FAILED:
        offsets = _retry_offsets()
        next_retry_at = datetime.now(UTC) + timedelta(
            days=offsets[min(payment.retry_count, len(offsets) - 1)]
        )
        payment.mark_failed(
            payload.failure_reason or "payment_failed", next_retry_at=next_retry_at
        )
        if payment.related_entity_id:
            if payment.payment_type == PaymentType.MEMBERSHIP:
                membership = session.get(GymMembership, payment.related_entity_id)
                if membership:
                    membership.status = GymMembershipStatus.INACTIVE
                    membership.ended_at = datetime.now(UTC)
                    session.add(membership)
            elif payment.payment_type == PaymentType.CLASS_BOOKING:
                booking = session.get(Booking, payment.related_entity_id)
                if booking and booking.status == BookingStatus.PENDING_PAYMENT:
                    booking.mark_cancelled()
                    # Release the held spot. Locked for the same reason the
                    # booking routes lock: this is a read-modify-write of
                    # spots_booked, and a booking request may be racing it.
                    class_session = session.exec(
                        select(ClassSession)
                        .where(ClassSession.id == booking.session_id)
                        .with_for_update()
                        .execution_options(populate_existing=True)
                    ).first()
                    if class_session and class_session.spots_booked > 0:
                        class_session.spots_booked -= 1
                        session.add(class_session)
                    session.add(booking)
            elif payment.payment_type == PaymentType.MARKETPLACE_SUBSCRIPTION:
                subscription = session.get(
                    MarketplaceSubscription, payment.related_entity_id
                )
                if (
                    subscription
                    and subscription.status
                    == MarketplaceSubscriptionStatus.PENDING_PAYMENT
                ):
                    subscription.status = MarketplaceSubscriptionStatus.CANCELLED
                    subscription.cancelled_at = datetime.now(UTC)
                    session.add(subscription)
    else:
        payment.status = payload.status

    # event_id is unique, so promote the audit row left by an earlier rejected
    # delivery rather than inserting a duplicate.
    event = rejected_event or PaymentWebhookEvent(
        event_id=payload.event_id, event_type=payload.event_type
    )
    event.provider = provider
    event.payment_id = payment.id
    event.event_type = payload.event_type
    event.signature_valid = True
    event.payload = payload.model_dump(mode="json", exclude_none=True)
    event.processed_at = datetime.now(UTC)
    session.add(payment)
    session.add(event)
    session.commit()
    return {"status": "processed"}


@router.get("/gyms/{gym_id}", response_model=GymPaymentsListResponse)
def gym_payment_dashboard(
    gym_id: UUID,
    _current_staff: StaffGymDep,
    session: SessionDep,
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    payment_type: PaymentType | None = Query(default=None),
    status: PaymentStatus | None = Query(default=None),
) -> GymPaymentsListResponse:
    query = select(Payment).where(Payment.gym_id == gym_id)
    if start_date:
        query = query.where(Payment.created_at >= start_date)
    if end_date:
        query = query.where(Payment.created_at <= end_date)
    if payment_type:
        query = query.where(Payment.payment_type == payment_type)
    if status:
        query = query.where(Payment.status == status)

    payments = list(session.exec(query).all())
    payments.sort(key=lambda p: p.created_at, reverse=True)
    consumer_ids = list({p.consumer_id for p in payments})
    names: dict[UUID, str] = {}
    for consumer_id in consumer_ids:
        consumer = session.get(Consumer, consumer_id)
        if consumer is not None:
            names[consumer.id] = f"{consumer.first_name} {consumer.last_name}".strip()

    summary = GymPaymentsSummary(
        total_received_cents=sum(
            p.amount_cents for p in payments if p.status == PaymentStatus.COMPLETED
        ),
        total_pending_cents=sum(
            p.amount_cents for p in payments if p.status == PaymentStatus.PENDING
        ),
        total_failed_cents=sum(
            p.amount_cents
            for p in payments
            if p.status in {PaymentStatus.FAILED, PaymentStatus.FAILED_PERMANENT}
        ),
    )
    items = [
        PaymentItem(
            payment_id=p.id,
            member_name=names.get(p.consumer_id, "Unknown Member"),
            amount_cents=p.amount_cents,
            currency=p.currency,
            payment_type=p.payment_type,
            status=p.status,
            created_at=p.created_at,
        )
        for p in payments
    ]
    return GymPaymentsListResponse(summary=summary, items=items)


@router.get("/gyms/{gym_id}/{payment_id}", response_model=GymPaymentDetailResponse)
def gym_payment_detail(
    gym_id: UUID,
    payment_id: UUID,
    _current_staff: StaffGymDep,
    session: SessionDep,
) -> GymPaymentDetailResponse:
    payment = session.get(Payment, payment_id)
    if not payment or payment.gym_id != gym_id:
        raise HTTPException(status_code=404, detail="Payment not found")

    consumer = session.get(Consumer, payment.consumer_id)
    member_name = (
        f"{consumer.first_name} {consumer.last_name}".strip()
        if consumer
        else "Unknown Member"
    )
    return GymPaymentDetailResponse(
        payment_id=payment.id,
        member_name=member_name,
        amount_cents=payment.amount_cents,
        currency=payment.currency,
        payment_type=payment.payment_type,
        status=payment.status,
        description=payment.description,
        provider=payment.provider,
        provider_reference=payment.provider_reference,
        failure_reason=payment.failure_reason,
        retry_count=payment.retry_count,
        created_at=payment.created_at,
        completed_at=payment.completed_at,
        failed_at=payment.failed_at,
    )


@router.get(
    "/gyms/{gym_id}/failed/action-items", response_model=list[FailedPaymentActionItem]
)
def failed_payment_action_items(
    gym_id: UUID, _current_staff: StaffGymDep, session: SessionDep
) -> list[FailedPaymentActionItem]:
    failed = [
        p
        for p in session.exec(select(Payment).where(Payment.gym_id == gym_id)).all()
        if p.status in {PaymentStatus.FAILED, PaymentStatus.FAILED_PERMANENT}
    ]
    items: list[FailedPaymentActionItem] = []
    for payment in failed:
        consumer = session.get(Consumer, payment.consumer_id)
        member_name = (
            f"{consumer.first_name} {consumer.last_name}".strip()
            if consumer
            else "Unknown Member"
        )
        items.append(
            FailedPaymentActionItem(
                payment_id=payment.id,
                member_name=member_name,
                failure_reason=payment.failure_reason,
                failed_at=payment.failed_at,
            )
        )
    return items


@router.post("/retries/run", response_model=RetryRunResponse)
def run_payment_retry_worker(session: SessionDep) -> RetryRunResponse:
    if settings.ENVIRONMENT != "local":
        raise HTTPException(status_code=404, detail="Not found")
    now = datetime.now(UTC)

    # --- Expire stale PENDING payments (abandoned checkouts, >1 hour old) ---
    stale_cutoff = now - timedelta(hours=1)
    stale_pending = list(
        session.exec(
            select(Payment).where(
                Payment.status == PaymentStatus.PENDING,
                Payment.created_at < stale_cutoff,
            )
        ).all()
    )
    for payment in stale_pending:
        payment.mark_failed("payment_expired", next_retry_at=None)
        payment.status = PaymentStatus.FAILED_PERMANENT
        if payment.related_entity_id:
            if payment.payment_type == PaymentType.MEMBERSHIP:
                membership = session.get(GymMembership, payment.related_entity_id)
                if (
                    membership
                    and membership.status == GymMembershipStatus.PENDING_PAYMENT
                ):
                    membership.status = GymMembershipStatus.CANCELLED
                    membership.is_active = False
                    membership.ended_at = now
                    session.add(membership)
            elif payment.payment_type == PaymentType.CLASS_BOOKING:
                booking = session.get(Booking, payment.related_entity_id)
                if booking and booking.status == BookingStatus.PENDING_PAYMENT:
                    booking.mark_cancelled()
                    class_session = session.get(ClassSession, booking.session_id)
                    if class_session and class_session.spots_booked > 0:
                        class_session.spots_booked -= 1
                        session.add(class_session)
                    session.add(booking)
            elif payment.payment_type == PaymentType.MARKETPLACE_SUBSCRIPTION:
                subscription = session.get(
                    MarketplaceSubscription, payment.related_entity_id
                )
                if (
                    subscription
                    and subscription.status
                    == MarketplaceSubscriptionStatus.PENDING_PAYMENT
                ):
                    subscription.status = MarketplaceSubscriptionStatus.CANCELLED
                    subscription.cancelled_at = now
                    session.add(subscription)
        session.add(payment)

    # --- Retry failed payments ---
    candidates = [
        p
        for p in session.exec(
            select(Payment).where(Payment.status == PaymentStatus.FAILED)
        ).all()
        if p.next_retry_at is not None and p.next_retry_at <= now
    ]

    offsets = _retry_offsets()
    processed: list[UUID] = []
    for payment in stale_pending:
        processed.append(payment.id)
    for payment in candidates:
        payment.retry_count += 1
        force_success = bool(payment.extra_data.get("force_success_on_retry"))
        if force_success:
            payment.mark_completed()
        elif payment.retry_count >= payment.max_retry_attempts:
            payment.status = PaymentStatus.FAILED_PERMANENT
            payment.next_retry_at = None
        else:
            payment.next_retry_at = now + timedelta(
                days=offsets[min(payment.retry_count, len(offsets) - 1)]
            )
        session.add(payment)
        processed.append(payment.id)

    session.commit()
    return RetryRunResponse(processed_payment_ids=processed)


@router.get(
    "/gyms/{gym_id}/reports/marketplace-payout", response_model=MarketplacePayoutReport
)
def marketplace_payout_report(
    gym_id: UUID,
    _current_staff: StaffGymDep,
    session: SessionDep,
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
) -> MarketplacePayoutReport:
    query = select(Payment).where(
        Payment.gym_id == gym_id,
        Payment.payment_type == PaymentType.CLASS_BOOKING,
        Payment.status == PaymentStatus.COMPLETED,
    )
    if start_date:
        query = query.where(Payment.created_at >= start_date)
    if end_date:
        query = query.where(Payment.created_at <= end_date)
    payments = session.exec(query).all()

    class_stats: dict[str, MarketplacePayoutClassBreakdown] = {}
    for p in payments:
        class_name = str(p.extra_data.get("class_name") or "Unspecified Class")
        if class_name not in class_stats:
            class_stats[class_name] = MarketplacePayoutClassBreakdown(
                class_name=class_name, bookings=0, gross_revenue_cents=0
            )
        class_stats[class_name].bookings += 1
        class_stats[class_name].gross_revenue_cents += p.amount_cents

    gross = sum(p.amount_cents for p in payments)
    fee = int(gross * 0.15)
    return MarketplacePayoutReport(
        total_marketplace_bookings=len(payments),
        gross_revenue_cents=gross,
        platform_fee_cents=fee,
        net_payout_cents=max(0, gross - fee),
        payout_schedule="Weekly settlement (every Monday)",
        class_breakdown=sorted(class_stats.values(), key=lambda x: x.class_name),
    )


@router.get("/me/history", response_model=ConsumerPaymentHistoryResponse)
def consumer_payment_history(
    current_consumer: CurrentConsumer,
    session: SessionDep,
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    payment_type: PaymentType | None = Query(default=None),
) -> ConsumerPaymentHistoryResponse:
    query = select(Payment).where(Payment.consumer_id == current_consumer.id)
    if start_date:
        query = query.where(Payment.created_at >= start_date)
    if end_date:
        query = query.where(Payment.created_at <= end_date)
    if payment_type:
        query = query.where(Payment.payment_type == payment_type)

    payments = list(session.exec(query).all())
    payments.sort(key=lambda p: p.created_at, reverse=True)
    receipt_map = {
        r.payment_id: r.id
        for r in session.exec(
            select(PaymentReceipt).where(
                PaymentReceipt.consumer_id == current_consumer.id
            )
        ).all()
    }

    return ConsumerPaymentHistoryResponse(
        items=[
            ConsumerPaymentHistoryItem(
                payment_id=p.id,
                description=p.description,
                amount_cents=p.amount_cents,
                currency=p.currency,
                payment_type=p.payment_type,
                status=p.status,
                created_at=p.created_at,
                receipt_id=receipt_map.get(p.id),
            )
            for p in payments
        ]
    )


@router.get("/me/{payment_id}/receipt", response_model=ReceiptResponse)
def get_or_generate_receipt(
    payment_id: UUID, current_consumer: CurrentConsumer, session: SessionDep
) -> ReceiptResponse:
    payment = session.get(Payment, payment_id)
    if not payment or payment.consumer_id != current_consumer.id:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Receipt can only be generated for completed payments",
        )

    receipt = session.exec(
        select(PaymentReceipt).where(PaymentReceipt.payment_id == payment.id)
    ).first()
    if not receipt:
        receipt = _build_receipt(payment, current_consumer)
        session.add(receipt)
        session.commit()
        session.refresh(receipt)

    return ReceiptResponse(
        receipt_id=receipt.id,
        payment_id=receipt.payment_id,
        receipt_number=receipt.receipt_number,
        rendered_text=receipt.rendered_text,
        subtotal_cents=receipt.subtotal_cents,
        vat_amount_cents=receipt.vat_amount_cents,
        total_cents=receipt.total_cents,
        vat_rate_percent=receipt.vat_rate_percent,
    )


@router.get("/webhook-signature-test")
def webhook_signature_test(
    event_id: str, payment_id: UUID, status: str
) -> dict[str, str]:
    if settings.ENVIRONMENT != "local":
        raise HTTPException(status_code=404, detail="Not found")
    return {"signature": build_webhook_signature(event_id, payment_id, status)}
