"""Authentication of the inbound payment webhook route.

Regression tests for the bypass where the webhook route took `provider` as a
path parameter, so the caller chose which verifier ran, and the PayFast stub
honoured a `verified: true` field in the request body. Together those let an
unauthenticated caller mark any payment completed, activate the membership and
issue a receipt with no secret and no signature.

The contract these tests pin down:

* `settings.PAYMENT_PROVIDER` decides the verifier; the URL never does.
* A `{provider}` path segment naming anything else is refused (403).
* A `{provider}` path segment naming nothing we implement is refused (404).
* A stub provider that cannot check a signature refuses outside an opted-in
  local dev machine, even when it is the configured provider.
* A genuine Stitch webhook with a valid Svix signature still succeeds.
"""

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlmodel import Session, select

from app.api.routes import payments as payments_route
from app.core.config import Settings
from app.models import (
    Gym,
    GymMembership,
    GymMembershipStatus,
    Payment,
    PaymentReceipt,
    PaymentStatus,
    PaymentType,
)
from app.services.payments.providers import (
    PayFastProvider,
    UnknownPaymentProviderError,
    get_default_payment_provider,
)
from tests.api.routes.test_staff_memberships import _consumer_headers

STITCH_SECRET_B64 = "dGVzdHNlY3JldA=="
STITCH_WEBHOOK_SECRET = f"whsec_{STITCH_SECRET_B64}"


def _pending_membership_payment(
    client: TestClient, db: Session
) -> tuple[Payment, GymMembership]:
    """A PENDING membership payment plus the INACTIVE membership it would activate.

    Returned as the target of a forged webhook: if the forgery is honoured the
    payment completes, the membership activates and a receipt is written, so the
    test can assert on all three.
    """
    _headers, consumer = _consumer_headers(client, db)
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    membership = GymMembership(
        gym_id=gym.id,
        consumer_id=consumer.id,
        status=GymMembershipStatus.INACTIVE,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)

    payment = Payment(
        gym_id=gym.id,
        consumer_id=consumer.id,
        amount_cents=49900,
        currency="ZAR",
        payment_type=PaymentType.MEMBERSHIP,
        status=PaymentStatus.PENDING,
        provider="payfast",
        description="Forgery target",
        related_entity_id=membership.id,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment, membership


def _assert_nothing_happened(
    db: Session, payment: Payment, membership: GymMembership
) -> None:
    db.refresh(payment)
    db.refresh(membership)
    assert payment.status == PaymentStatus.PENDING
    assert membership.status == GymMembershipStatus.INACTIVE
    receipt = db.exec(
        select(PaymentReceipt).where(PaymentReceipt.payment_id == payment.id)
    ).first()
    assert receipt is None


# =============================================================================
# The forged request
# =============================================================================


def test_forged_payfast_webhook_with_verified_flag_is_rejected(
    client: TestClient, db: Session
) -> None:
    """The original exploit: POST /webhooks/payfast with {"verified": true}.

    PAYMENT_PROVIDER is 'ozow' in the test environment, so naming payfast in the
    path must be refused outright, and the magic flag must do nothing.
    """
    payment, membership = _pending_membership_payment(client, db)

    res = client.post(
        "/api/v1/payments/webhooks/payfast",
        json={
            "event_id": f"forged-{uuid4()}",
            "payment_id": str(payment.id),
            "status": "completed",
            "verified": True,
            "provider_reference": "forged-ref",
        },
    )

    assert res.status_code in (401, 403), res.text
    _assert_nothing_happened(db, payment, membership)


def test_forged_webhook_on_bare_route_without_signature_is_rejected(
    client: TestClient, db: Session
) -> None:
    """The same forgery against /payments/webhook, with no signature header."""
    payment, membership = _pending_membership_payment(client, db)

    res = client.post(
        "/api/v1/payments/webhook",
        json={
            "event_id": f"forged-{uuid4()}",
            "payment_id": str(payment.id),
            "status": "completed",
            "verified": True,
        },
    )

    assert res.status_code != 200, res.text
    assert res.status_code in (400, 401, 403), res.text
    _assert_nothing_happened(db, payment, membership)


def test_verified_is_not_a_field_on_the_webhook_schema() -> None:
    """Nothing in the request body may assert its own authenticity."""
    assert "verified" not in payments_route.PaymentWebhookRequest.model_fields


def test_verified_in_the_body_never_reaches_a_verifier(
    client: TestClient, db: Session, monkeypatch
) -> None:
    """Even if a caller sends it, `verified` is dropped before verification."""
    captured: dict[str, object] = {}

    class _Capturing:
        can_verify_webhooks = True

        def verify(self, payload, signature=None):
            captured.update(payload)

            class _R:
                is_valid = False
                provider_reference = None
                failure_reason = "nope"

            return _R()

    monkeypatch.setattr(
        payments_route, "get_payment_provider", lambda _name: _Capturing()
    )
    payment, membership = _pending_membership_payment(client, db)

    res = client.post(
        "/api/v1/payments/webhooks/ozow",
        json={
            "event_id": f"forged-{uuid4()}",
            "payment_id": str(payment.id),
            "status": "completed",
            "verified": True,
        },
    )

    assert res.status_code == 400, res.text
    assert captured, "verifier was never called"
    assert "verified" not in captured
    _assert_nothing_happened(db, payment, membership)


# =============================================================================
# Provider resolution
# =============================================================================


def test_unknown_provider_path_is_rejected(client: TestClient, db: Session) -> None:
    payment, membership = _pending_membership_payment(client, db)

    res = client.post(
        "/api/v1/payments/webhooks/definitely-not-a-provider",
        json={
            "event_id": f"evt-{uuid4()}",
            "payment_id": str(payment.id),
            "status": "completed",
        },
    )

    assert res.status_code == 404, res.text
    _assert_nothing_happened(db, payment, membership)


def test_provider_path_that_is_not_the_configured_provider_is_rejected(
    client: TestClient, db: Session, monkeypatch
) -> None:
    """A valid provider name in the URL still cannot override the configuration."""
    monkeypatch.setattr(payments_route.settings, "PAYMENT_PROVIDER", "ozow")
    payment, membership = _pending_membership_payment(client, db)

    res = client.post(
        "/api/v1/payments/webhooks/stitch",
        json={
            "event_id": f"evt-{uuid4()}",
            "payment_id": str(payment.id),
            "status": "completed",
        },
    )

    assert res.status_code == 403, res.text
    _assert_nothing_happened(db, payment, membership)


def test_unrecognised_configured_provider_is_not_silently_ozow(monkeypatch) -> None:
    """A typo in PAYMENT_PROVIDER must fail loudly, not fall back to Ozow."""
    monkeypatch.setattr(payments_route.settings, "PAYMENT_PROVIDER", "ozoww")
    with pytest.raises(UnknownPaymentProviderError):
        get_default_payment_provider()

    monkeypatch.setattr(payments_route.settings, "PAYMENT_PROVIDER", "")
    with pytest.raises(UnknownPaymentProviderError):
        get_default_payment_provider()


def test_misconfigured_provider_makes_the_route_refuse(
    client: TestClient, db: Session, monkeypatch
) -> None:
    monkeypatch.setattr(payments_route.settings, "PAYMENT_PROVIDER", "ozoww")
    payment, membership = _pending_membership_payment(client, db)

    res = client.post(
        "/api/v1/payments/webhook",
        json={
            "event_id": f"evt-{uuid4()}",
            "payment_id": str(payment.id),
            "status": "completed",
        },
    )

    assert res.status_code == 503, res.text
    _assert_nothing_happened(db, payment, membership)


# =============================================================================
# The stub provider refuses on its own account
# =============================================================================


def test_configured_stub_provider_refuses_without_the_local_opt_in(
    client: TestClient, db: Session, monkeypatch
) -> None:
    """Even as the configured provider, PayFast cannot accept a webhook."""
    monkeypatch.setattr(payments_route.settings, "PAYMENT_PROVIDER", "payfast")
    monkeypatch.setattr(
        payments_route.settings, "PAYMENT_ALLOW_UNVERIFIED_STUB_WEBHOOKS", False
    )
    payment, membership = _pending_membership_payment(client, db)

    res = client.post(
        "/api/v1/payments/webhooks/payfast",
        json={
            "event_id": f"evt-{uuid4()}",
            "payment_id": str(payment.id),
            "status": "completed",
            "verified": True,
        },
    )

    assert res.status_code == 403, res.text
    _assert_nothing_happened(db, payment, membership)


def test_payfast_verify_refuses_outside_local_even_with_the_flag_on(
    monkeypatch,
) -> None:
    """Both halves of the gate are re-read, so a mutated setting is not enough."""
    from app.services.payments import providers as providers_mod

    monkeypatch.setattr(
        providers_mod.settings, "PAYMENT_ALLOW_UNVERIFIED_STUB_WEBHOOKS", True
    )
    for environment in ("staging", "production"):
        monkeypatch.setattr(providers_mod.settings, "ENVIRONMENT", environment)
        result = PayFastProvider().verify({"verified": True}, signature="whatever")
        assert result.is_valid is False
        assert result.failure_reason == "stub_provider_cannot_verify_signature"


def test_payfast_verify_refuses_in_local_without_the_flag(monkeypatch) -> None:
    from app.services.payments import providers as providers_mod

    monkeypatch.setattr(providers_mod.settings, "ENVIRONMENT", "local")
    monkeypatch.setattr(
        providers_mod.settings, "PAYMENT_ALLOW_UNVERIFIED_STUB_WEBHOOKS", False
    )
    assert PayFastProvider().verify({"verified": True}).is_valid is False


def test_settings_refuse_the_stub_opt_in_outside_local() -> None:
    """The opt-in cannot be set at all in staging or production."""
    base = {
        "PROJECT_NAME": "studioloop-test",
        "SECRET_KEY": "a-real-secret-key-for-this-test",
        "POSTGRES_SERVER": "localhost",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "not-the-default",
        "POSTGRES_DB": "app",
        "FIRST_SUPERUSER": "admin@example.com",
        "FIRST_SUPERUSER_PASSWORD": "not-the-default",
        "STITCH_WEBHOOK_SECRET": STITCH_WEBHOOK_SECRET,
        "PAYMENT_PROVIDER": "stitch",
        "PAYMENT_ALLOW_UNVERIFIED_STUB_WEBHOOKS": True,
    }
    for environment in ("staging", "production"):
        with pytest.raises(ValidationError) as excinfo:
            Settings(_env_file=None, ENVIRONMENT=environment, **base)
        assert "PAYMENT_ALLOW_UNVERIFIED_STUB_WEBHOOKS" in str(excinfo.value)

    # Same values are accepted in local.
    local = Settings(_env_file=None, ENVIRONMENT="local", **base)
    assert local.PAYMENT_ALLOW_UNVERIFIED_STUB_WEBHOOKS is True


def test_settings_reject_an_unknown_payment_provider() -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            PROJECT_NAME="studioloop-test",
            FIRST_SUPERUSER="admin@example.com",
            FIRST_SUPERUSER_PASSWORD="not-the-default",
            POSTGRES_PASSWORD="not-the-default",
            PAYMENT_PROVIDER="ozoww",
        )


# =============================================================================
# The genuine article still works
# =============================================================================


def test_genuine_stitch_webhook_with_valid_signature_succeeds(
    client: TestClient, db: Session, monkeypatch
) -> None:
    """A real Svix-signed Stitch delivery completes the payment end to end."""
    monkeypatch.setattr(payments_route.settings, "PAYMENT_PROVIDER", "stitch")
    monkeypatch.setattr(
        payments_route.settings, "STITCH_WEBHOOK_SECRET", STITCH_WEBHOOK_SECRET
    )
    payment, membership = _pending_membership_payment(client, db)

    body = json.dumps(
        {
            "event_id": f"evt-{uuid4()}",
            "payment_id": str(payment.id),
            "status": "completed",
            "provider_reference": "pir_genuine_123",
        },
        separators=(",", ":"),
    )
    svix_id = f"msg_{uuid4().hex[:12]}"
    svix_timestamp = str(int(datetime.now(UTC).timestamp()))
    signature = base64.b64encode(
        hmac.new(
            base64.b64decode(STITCH_SECRET_B64),
            f"{svix_id}.{svix_timestamp}.{body}".encode(),
            hashlib.sha256,
        ).digest()
    ).decode()

    res = client.post(
        "/api/v1/payments/webhooks/stitch",
        content=body,
        headers={
            "content-type": "application/json",
            "svix-id": svix_id,
            "svix-timestamp": svix_timestamp,
            "svix-signature": f"v1,{signature}",
        },
    )

    assert res.status_code == 200, res.text
    assert res.json()["status"] == "processed"

    db.refresh(payment)
    db.refresh(membership)
    assert payment.status == PaymentStatus.COMPLETED
    assert membership.status == GymMembershipStatus.ACTIVE


def test_genuine_ozow_webhook_with_valid_signature_still_succeeds(
    client: TestClient, db: Session, monkeypatch
) -> None:
    """The configured provider's own signature scheme keeps working."""
    monkeypatch.setattr(payments_route.settings, "PAYMENT_PROVIDER", "ozow")
    payment, membership = _pending_membership_payment(client, db)

    event_id = f"evt-{uuid4()}"
    signature = payments_route.build_webhook_signature(
        event_id, payment.id, "completed"
    )

    res = client.post(
        "/api/v1/payments/webhooks/ozow",
        json={
            "event_id": event_id,
            "payment_id": str(payment.id),
            "status": "completed",
            "provider_reference": "ozow-ref-ok",
        },
        headers={"X-Signature": signature},
    )

    assert res.status_code == 200, res.text
    db.refresh(payment)
    db.refresh(membership)
    assert payment.status == PaymentStatus.COMPLETED
    assert membership.status == GymMembershipStatus.ACTIVE


def test_rejected_event_id_does_not_suppress_the_real_delivery(
    client: TestClient, db: Session, monkeypatch
) -> None:
    """A bad-signature attempt must not burn the event_id for the real webhook.

    Idempotency used to key on event_id alone, so an unauthenticated caller
    could guess or replay an event_id, get a 400, and have the genuine delivery
    answered 'already_processed' without ever being applied.
    """
    monkeypatch.setattr(payments_route.settings, "PAYMENT_PROVIDER", "ozow")
    payment, membership = _pending_membership_payment(client, db)

    event_id = f"evt-{uuid4()}"
    body = {
        "event_id": event_id,
        "payment_id": str(payment.id),
        "status": "completed",
        "provider_reference": "ozow-ref-ok",
    }

    forged = client.post(
        "/api/v1/payments/webhooks/ozow",
        json=body,
        headers={"X-Signature": "0" * 64},
    )
    assert forged.status_code == 400, forged.text
    _assert_nothing_happened(db, payment, membership)

    genuine = client.post(
        "/api/v1/payments/webhooks/ozow",
        json=body,
        headers={
            "X-Signature": payments_route.build_webhook_signature(
                event_id, UUID(str(payment.id)), "completed"
            )
        },
    )
    assert genuine.status_code == 200, genuine.text
    assert genuine.json()["status"] == "processed"

    db.refresh(payment)
    db.refresh(membership)
    assert payment.status == PaymentStatus.COMPLETED
    assert membership.status == GymMembershipStatus.ACTIVE
