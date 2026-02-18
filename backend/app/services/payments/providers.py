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


class PaymentProvider(Protocol):
    provider_name: PaymentProviderName

    def initiate(self, payment: Payment) -> PaymentInitiationResult: ...

    def verify(self, payload: dict[str, str | int | bool | None], signature: str | None = None) -> PaymentVerificationResult: ...

    def refund(self, payment: Payment, amount_cents: int | None = None) -> PaymentVerificationResult: ...


class OzowProvider:
    provider_name = PaymentProviderName.OZOW

    def initiate(self, payment: Payment) -> PaymentInitiationResult:
        reference = f"ozow-{payment.id}"
        return PaymentInitiationResult(
            provider_reference=reference,
            redirect_url=f"https://payments.ozow.example/checkout/{payment.id}",
        )

    def verify(self, payload: dict[str, str | int | bool | None], signature: str | None = None) -> PaymentVerificationResult:
        secret = settings.SECRET_KEY.encode()
        event_id = str(payload.get("event_id", ""))
        payment_id = str(payload.get("payment_id", ""))
        status = str(payload.get("status", "")).lower()
        expected = hmac.new(secret, f"{event_id}:{payment_id}:{status}".encode(), sha256).hexdigest()
        valid = signature is not None and compare_digest(signature, expected)
        return PaymentVerificationResult(is_valid=valid, provider_reference=str(payload.get("provider_reference") or ""))

    def refund(self, payment: Payment, amount_cents: int | None = None) -> PaymentVerificationResult:
        return PaymentVerificationResult(is_valid=True, provider_reference=f"ozow-refund-{payment.id}")


class PayFastProvider:
    provider_name = PaymentProviderName.PAYFAST

    def initiate(self, payment: Payment) -> PaymentInitiationResult:
        reference = f"payfast-{payment.id}"
        return PaymentInitiationResult(
            provider_reference=reference,
            redirect_url=f"https://sandbox.payfast.example/eng/process?reference={payment.id}",
        )

    def verify(self, payload: dict[str, str | int | bool | None], signature: str | None = None) -> PaymentVerificationResult:
        # MVP stub verifier: explicit flag for testability
        verified = bool(payload.get("verified", False))
        return PaymentVerificationResult(
            is_valid=verified,
            provider_reference=str(payload.get("provider_reference") or ""),
            failure_reason=None if verified else "signature_verification_failed",
        )

    def refund(self, payment: Payment, amount_cents: int | None = None) -> PaymentVerificationResult:
        return PaymentVerificationResult(is_valid=True, provider_reference=f"payfast-refund-{payment.id}")


def get_payment_provider(name: PaymentProviderName) -> PaymentProvider:
    if name == PaymentProviderName.PAYFAST:
        return PayFastProvider()
    return OzowProvider()


def get_default_payment_provider() -> PaymentProviderName:
    configured = getattr(settings, "PAYMENT_PROVIDER", PaymentProviderName.OZOW.value)
    if configured == PaymentProviderName.PAYFAST.value:
        return PaymentProviderName.PAYFAST
    return PaymentProviderName.OZOW


def build_webhook_signature(event_id: str, payment_id: UUID, status: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(),
        f"{event_id}:{payment_id}:{status.lower()}".encode(),
        sha256,
    ).hexdigest()
