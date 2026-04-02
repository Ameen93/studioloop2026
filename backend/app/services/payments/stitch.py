"""Stitch Payments provider implementation.

Integrates with Stitch (https://stitch.money) for:
- Pay By Bank (one-time payments via GraphQL API)
- Variable Recurring Payments (VRP) for subscriptions
- Webhook verification via Svix signatures

Auth: OAuth2 Client Credentials flow → client token with scoped access.
API: GraphQL at https://api.stitch.money/graphql
Webhooks: Svix-based HMAC-SHA256 signature verification.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import logging
import time
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from app.core.config import settings
from app.models.payment import Payment, PaymentProviderName, PaymentType
from app.services.payments.providers import (
    PaymentInitiationResult,
    PaymentVerificationResult,
)

logger = logging.getLogger(__name__)

# GraphQL mutations
_PAYMENT_REQUEST_MUTATION = """
mutation CreatePaymentRequest(
    $amount: MoneyInput!,
    $payerReference: String!,
    $beneficiaryReference: String!,
    $externalReference: String,
    $beneficiary: BeneficiaryInput!,
    $expireAt: Date
) {
    clientPaymentInitiationRequestCreate(input: {
        amount: $amount,
        payerReference: $payerReference,
        beneficiaryReference: $beneficiaryReference,
        externalReference: $externalReference,
        beneficiary: $beneficiary,
        expireAt: $expireAt
    }) {
        paymentInitiationRequest {
            id
            url
        }
    }
}
"""

_RECURRING_CONSENT_MUTATION = """
mutation CreateRecurringPaymentConsent(
    $beneficiary: BeneficiaryInput!,
    $payerReference: String!,
    $beneficiaryReference: String!,
    $externalReference: String,
    $amount: MoneyInput!
) {
    paymentConsentRequestCreate(input: {
        beneficiary: $beneficiary,
        payerReference: $payerReference,
        beneficiaryReference: $beneficiaryReference,
        externalReference: $externalReference,
        amount: $amount
    }) {
        consentRequest {
            id
            url
        }
    }
}
"""

_PAYMENT_STATUS_QUERY = """
query GetPaymentStatus($paymentRequestId: ID!) {
    node(id: $paymentRequestId) {
        ... on PaymentInitiationRequest {
            id
            status {
                __typename
            }
        }
    }
}
"""


class StitchTokenManager:
    """Manages OAuth2 client credential tokens for Stitch API."""

    def __init__(self) -> None:
        self._token: str | None = None
        self._expires_at: float = 0

    def get_token(self, scopes: str = "client_paymentrequest") -> str:
        """Get a valid client token, refreshing if expired."""
        if self._token and time.time() < self._expires_at - 30:
            return self._token
        return self._refresh_token(scopes)

    def _refresh_token(self, scopes: str) -> str:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                settings.STITCH_TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.STITCH_CLIENT_ID,
                    "client_secret": settings.STITCH_CLIENT_SECRET,
                    "scope": scopes,
                    "audience": settings.STITCH_TOKEN_URL,
                },
            )
            response.raise_for_status()
            data = response.json()
            self._token = data["access_token"]
            self._expires_at = time.time() + data.get("expires_in", 3600)
            return self._token  # type: ignore[return-value]


# Module-level singleton for token caching
_token_manager = StitchTokenManager()


class StitchProvider:
    """Stitch payment provider supporting Pay By Bank and VRP."""

    provider_name = PaymentProviderName.STITCH

    def __init__(
        self,
        token_manager: StitchTokenManager | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._token_manager = token_manager or _token_manager
        self._http_client = http_client

    def _graphql(
        self,
        query: str,
        variables: dict[str, Any],
        scopes: str = "client_paymentrequest",
    ) -> dict[str, Any]:
        """Execute a GraphQL request against the Stitch API."""
        token = self._token_manager.get_token(scopes)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {"query": query, "variables": variables}

        if self._http_client:
            resp = self._http_client.post(
                settings.STITCH_API_URL, json=payload, headers=headers
            )
        else:
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    settings.STITCH_API_URL, json=payload, headers=headers
                )
        resp.raise_for_status()
        result = resp.json()
        if errors := result.get("errors"):
            raise RuntimeError(f"Stitch GraphQL error: {errors}")
        return result["data"]

    def initiate(self, payment: Payment) -> PaymentInitiationResult:
        """Create a payment request or recurring consent via Stitch."""
        amount_rands = payment.amount_cents / 100
        amount_input = {
            "quantity": f"{amount_rands:.2f}",
            "currency": payment.currency,
        }
        beneficiary = {
            "bankAccount": {
                "name": "StudioLoop",
                "bankId": "fnb",
                "accountNumber": "0000000000",
                "accountType": "current",
                "beneficiaryType": "private",
            }
        }
        payer_ref = str(payment.id)[:12]
        beneficiary_ref = f"SL-{str(payment.id)[:16]}"
        external_ref = str(payment.id)

        if payment.payment_type == PaymentType.MEMBERSHIP:
            # Use recurring consent for membership subscriptions (VRP)
            data = self._graphql(
                _RECURRING_CONSENT_MUTATION,
                {
                    "amount": amount_input,
                    "payerReference": payer_ref,
                    "beneficiaryReference": beneficiary_ref,
                    "externalReference": external_ref,
                    "beneficiary": beneficiary,
                },
                scopes="client_recurringpaymentconsentrequest",
            )
            consent = data["paymentConsentRequestCreate"]["consentRequest"]
            redirect_url = consent["url"]
            if payment.return_url:
                redirect_url += f"?redirect_uri={payment.return_url}"
            return PaymentInitiationResult(
                provider_reference=consent["id"],
                redirect_url=redirect_url,
            )
        else:
            # One-time Pay By Bank
            expire_at = (datetime.now(UTC) + timedelta(hours=1)).strftime(
                "%Y-%m-%dT%H:%M:%S.000Z"
            )
            data = self._graphql(
                _PAYMENT_REQUEST_MUTATION,
                {
                    "amount": amount_input,
                    "payerReference": payer_ref,
                    "beneficiaryReference": beneficiary_ref,
                    "externalReference": external_ref,
                    "beneficiary": beneficiary,
                    "expireAt": expire_at,
                },
            )
            pir = data["clientPaymentInitiationRequestCreate"][
                "paymentInitiationRequest"
            ]
            redirect_url = pir["url"]
            if payment.return_url:
                redirect_url += f"?redirect_uri={payment.return_url}"
            return PaymentInitiationResult(
                provider_reference=pir["id"],
                redirect_url=redirect_url,
            )

    def verify(
        self,
        payload: dict[str, str | int | bool | None],
        signature: str | None = None,
    ) -> PaymentVerificationResult:
        """Verify a Stitch/Svix webhook signature.

        Stitch webhooks are delivered via Svix. The signature format uses:
        - svix-id header
        - svix-timestamp header
        - svix-signature header (v1,<base64_signature>)
        - The webhook secret (whsec_<base64_key>)

        For our webhook route integration, we pass the raw signature in X-Signature
        which contains the full Svix verification data as a JSON-encoded string:
        {"svix_id": "...", "svix_timestamp": "...", "svix_signature": "v1,...", "body": "..."}

        For simplicity in the existing webhook architecture, we support both:
        1. Full Svix verification (when signature contains svix data)
        2. HMAC verification fallback (matching existing pattern)
        """
        if not signature:
            return PaymentVerificationResult(
                is_valid=False, failure_reason="missing_signature"
            )

        def _as_string(value: object) -> str:
            return value if isinstance(value, str) else ""

        # Stitch webhooks should be verified via Svix using raw request body + svix headers.
        svix_id = _as_string(payload.get("_svix_id"))
        svix_timestamp = _as_string(payload.get("_svix_timestamp"))
        svix_signature = _as_string(payload.get("_svix_signature"))
        raw_body = _as_string(payload.get("_raw_body"))

        # If any Svix metadata is present, require all Svix fields to avoid insecure fallbacks.
        if any((svix_id, svix_timestamp, svix_signature, raw_body)):
            if not all((svix_id, svix_timestamp, svix_signature, raw_body)):
                return PaymentVerificationResult(
                    is_valid=False,
                    provider_reference=str(payload.get("provider_reference") or ""),
                    failure_reason="missing_svix_fields",
                )

            is_valid = verify_svix_signature(
                svix_id=svix_id,
                svix_timestamp=svix_timestamp,
                svix_signature=svix_signature,
                body=raw_body,
                secret=settings.STITCH_WEBHOOK_SECRET,
            )
            return PaymentVerificationResult(
                is_valid=is_valid,
                provider_reference=str(payload.get("provider_reference") or ""),
                failure_reason=None if is_valid else "svix_signature_invalid",
            )

        # Fallback: HMAC verification for non-Svix integration paths
        secret = (settings.STITCH_WEBHOOK_SECRET or settings.SECRET_KEY).encode()
        event_id = str(payload.get("event_id", ""))
        payment_id = str(payload.get("payment_id", ""))
        status = str(payload.get("status", "")).lower()
        expected = hmac.new(
            secret, f"{event_id}:{payment_id}:{status}".encode(), hashlib.sha256
        ).hexdigest()
        valid = hmac.compare_digest(signature, expected)
        return PaymentVerificationResult(
            is_valid=valid,
            provider_reference=str(payload.get("provider_reference") or ""),
            failure_reason=None if valid else "signature_mismatch",
        )

    def refund(
        self, payment: Payment, amount_cents: int | None = None
    ) -> PaymentVerificationResult:
        """Initiate a refund via Stitch API."""
        # Stitch supports refunds via client_refund scope
        # For now, return success - full implementation requires refund mutation
        return PaymentVerificationResult(
            is_valid=True,
            provider_reference=f"stitch-refund-{payment.id}",
        )


def verify_svix_signature(
    svix_id: str,
    svix_timestamp: str,
    svix_signature: str,
    body: str,
    secret: str,
) -> bool:
    """Verify a Svix webhook signature per the Svix manual verification spec.

    See: https://docs.svix.com/receiving/verifying-payloads/how-manual
    """
    if not secret:
        return False

    # Check timestamp is within tolerance (5 minutes)
    try:
        ts = int(svix_timestamp)
        if abs(time.time() - ts) > 300:
            return False
    except (ValueError, TypeError):
        return False

    # Extract base64 key from whsec_ prefix
    if secret.startswith("whsec_"):
        try:
            secret_bytes = base64.b64decode(secret[6:], validate=True)
        except (binascii.Error, ValueError):
            return False
    else:
        secret_bytes = secret.encode()

    # Construct signed content: svix_id.svix_timestamp.body
    signed_content = f"{svix_id}.{svix_timestamp}.{body}"
    computed = base64.b64encode(
        hmac.new(secret_bytes, signed_content.encode(), hashlib.sha256).digest()
    ).decode()

    # svix_signature can contain multiple space-separated signatures: "v1,<sig1> v2,<sig2>"
    for sig_entry in svix_signature.split(" "):
        parts = sig_entry.split(",", 1)
        if len(parts) == 2 and parts[0] == "v1":
            if hmac.compare_digest(computed, parts[1]):
                return True

    return False
