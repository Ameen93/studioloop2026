from __future__ import annotations

import hmac
from dataclasses import dataclass
from hashlib import sha256
from hmac import compare_digest
from typing import Protocol
from uuid import UUID

from app.core.config import settings
from app.models.payment import Payment, PaymentProviderName


@dataclass
class PaymentInitiationResult:
    provider_reference: str
    redirect_url: str


@dataclass
class PaymentVerificationResult:
    is_valid: bool
    provider_reference: str | None = None
    failure_reason: str | None = None


class UnknownPaymentProviderError(ValueError):
    """Raised when settings name a payment provider we have no implementation for."""


def stub_webhooks_allowed() -> bool:
    """Whether a provider with no signing secret may still accept webhooks.

    Only ever true on a local development machine that has explicitly opted in.
    Settings validation refuses PAYMENT_ALLOW_UNVERIFIED_STUB_WEBHOOKS outside
    ENVIRONMENT=local, and re-reading both values here means a mutated or
    monkeypatched setting still cannot enable stub acceptance in staging or
    production.
    """
    return bool(
        settings.ENVIRONMENT == "local"
        and settings.PAYMENT_ALLOW_UNVERIFIED_STUB_WEBHOOKS
    )


class PaymentProvider(Protocol):
    provider_name: PaymentProviderName
    # False for stub providers that hold no signing secret and therefore cannot
    # authenticate an inbound webhook at all.
    can_verify_webhooks: bool

    def initiate(self, payment: Payment) -> PaymentInitiationResult: ...

    def verify(
        self, payload: dict[str, str | int | bool | None], signature: str | None = None
    ) -> PaymentVerificationResult: ...

    def refund(
        self, payment: Payment, amount_cents: int | None = None
    ) -> PaymentVerificationResult: ...


class OzowProvider:
    provider_name = PaymentProviderName.OZOW
    # Verifies an HMAC-SHA256 digest keyed on SECRET_KEY, so a caller without the
    # shared secret cannot forge a webhook.
    can_verify_webhooks = True

    def initiate(self, payment: Payment) -> PaymentInitiationResult:
        reference = f"ozow-{payment.id}"
        return PaymentInitiationResult(
            provider_reference=reference,
            redirect_url=f"https://payments.ozow.example/checkout/{payment.id}",
        )

    def verify(
        self, payload: dict[str, str | int | bool | None], signature: str | None = None
    ) -> PaymentVerificationResult:
        secret = settings.SECRET_KEY.encode()
        event_id = str(payload.get("event_id", ""))
        payment_id = str(payload.get("payment_id", ""))
        status = str(payload.get("status", "")).lower()
        expected = hmac.new(
            secret, f"{event_id}:{payment_id}:{status}".encode(), sha256
        ).hexdigest()
        valid = signature is not None and compare_digest(signature, expected)
        return PaymentVerificationResult(
            is_valid=valid,
            provider_reference=str(payload.get("provider_reference") or ""),
        )

    def refund(
        self, payment: Payment, amount_cents: int | None = None
    ) -> PaymentVerificationResult:
        return PaymentVerificationResult(
            is_valid=True, provider_reference=f"ozow-refund-{payment.id}"
        )


class PayFastProvider:
    """Stub PayFast provider. PayFast's real signature scheme is not implemented.

    Because it holds no signing secret it cannot authenticate anything, so it
    refuses every webhook unless this is a local development machine that has
    opted in via PAYMENT_ALLOW_UNVERIFIED_STUB_WEBHOOKS. It used to honour a
    `verified: true` field supplied by the caller, which made the webhook route
    an unauthenticated way to mark any payment completed.
    """

    provider_name = PaymentProviderName.PAYFAST
    can_verify_webhooks = False

    def initiate(self, payment: Payment) -> PaymentInitiationResult:
        reference = f"payfast-{payment.id}"
        return PaymentInitiationResult(
            provider_reference=reference,
            redirect_url=f"https://sandbox.payfast.example/eng/process?reference={payment.id}",
        )

    def verify(
        self, payload: dict[str, str | int | bool | None], signature: str | None = None
    ) -> PaymentVerificationResult:
        if not stub_webhooks_allowed():
            return PaymentVerificationResult(
                is_valid=False,
                provider_reference=str(payload.get("provider_reference") or ""),
                failure_reason="stub_provider_cannot_verify_signature",
            )
        return PaymentVerificationResult(
            is_valid=True,
            provider_reference=str(payload.get("provider_reference") or ""),
            failure_reason=None,
        )

    def refund(
        self, payment: Payment, amount_cents: int | None = None
    ) -> PaymentVerificationResult:
        return PaymentVerificationResult(
            is_valid=True, provider_reference=f"payfast-refund-{payment.id}"
        )


def get_payment_provider(name: PaymentProviderName) -> PaymentProvider:
    if name == PaymentProviderName.PAYFAST:
        return PayFastProvider()
    if name == PaymentProviderName.STITCH:
        from app.services.payments.stitch import StitchProvider

        return StitchProvider()
    if name == PaymentProviderName.OZOW:
        return OzowProvider()
    raise UnknownPaymentProviderError(
        f"No payment provider implementation for {name!r}"
    )


def get_default_payment_provider() -> PaymentProviderName:
    """Return the single provider named by settings.

    Raises UnknownPaymentProviderError rather than falling back to Ozow: a typo
    or an empty PAYMENT_PROVIDER must be a loud failure, not a silent switch to
    a different provider's verifier.
    """
    configured = str(getattr(settings, "PAYMENT_PROVIDER", "") or "").strip().lower()
    if not configured:
        raise UnknownPaymentProviderError("PAYMENT_PROVIDER is not configured")
    try:
        return PaymentProviderName(configured)
    except ValueError:
        raise UnknownPaymentProviderError(
            f"PAYMENT_PROVIDER={configured!r} is not a known payment provider"
        ) from None


def build_webhook_signature(event_id: str, payment_id: UUID, status: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(),
        f"{event_id}:{payment_id}:{status.lower()}".encode(),
        sha256,
    ).hexdigest()
