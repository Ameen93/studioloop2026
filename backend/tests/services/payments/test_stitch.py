"""Tests for the Stitch Payments provider.

All external API calls are mocked — no real network requests.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import time
from unittest.mock import MagicMock, patch
from uuid import uuid4

import httpx
import pytest

from app.models.payment import (
    Payment,
    PaymentProviderName,
    PaymentStatus,
    PaymentType,
)
from app.services.payments.stitch import (
    StitchProvider,
    StitchTokenManager,
    verify_svix_signature,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_payment(
    payment_type: PaymentType = PaymentType.CLASS_BOOKING,
    amount_cents: int = 15000,
) -> Payment:
    """Create an in-memory Payment (not persisted)."""
    return Payment.model_validate(
        {
            "id": uuid4(),
            "gym_id": uuid4(),
            "consumer_id": uuid4(),
            "amount_cents": amount_cents,
            "currency": "ZAR",
            "payment_type": payment_type,
            "status": PaymentStatus.PENDING,
            "provider": PaymentProviderName.STITCH,
            "description": "Test payment",
            "return_url": "https://app.test/return",
            "cancel_url": "https://app.test/cancel",
            "webhook_url": "https://api.test/webhook",
            "related_entity_id": None,
            "extra_data": {},
        }
    )


def _mock_token_manager() -> StitchTokenManager:
    mgr = StitchTokenManager()
    mgr._token = "mock-access-token"
    mgr._expires_at = time.time() + 3600
    return mgr


def _make_svix_signature(
    body: str, secret: str = "whsec_dGVzdHNlY3JldA=="
) -> tuple[str, str, str]:
    """Generate valid Svix signature components."""
    svix_id = "msg_test123"
    svix_timestamp = str(int(time.time()))
    secret_bytes = base64.b64decode(secret[6:])
    signed_content = f"{svix_id}.{svix_timestamp}.{body}"
    sig = base64.b64encode(
        hmac.new(secret_bytes, signed_content.encode(), hashlib.sha256).digest()
    ).decode()
    return svix_id, svix_timestamp, f"v1,{sig}"


# ---------------------------------------------------------------------------
# Token Manager
# ---------------------------------------------------------------------------


class TestStitchTokenManager:
    def test_get_token_caches(self) -> None:
        mgr = _mock_token_manager()
        assert mgr.get_token() == "mock-access-token"

    @patch("app.services.payments.stitch.settings")
    def test_refresh_token(self, mock_settings: MagicMock) -> None:
        mock_settings.STITCH_TOKEN_URL = "https://secure.stitch.money/connect/token"
        mock_settings.STITCH_CLIENT_ID = "test-client"
        mock_settings.STITCH_CLIENT_SECRET = "test-secret"

        mgr = StitchTokenManager()
        mgr._expires_at = 0  # force refresh

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "fresh-token",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.Client") as MockClient:
            MockClient.return_value.__enter__ = MagicMock(
                return_value=MagicMock(post=MagicMock(return_value=mock_response))
            )
            MockClient.return_value.__exit__ = MagicMock(return_value=False)
            token = mgr.get_token("client_paymentrequest")

        assert token == "fresh-token"
        assert mgr._token == "fresh-token"


# ---------------------------------------------------------------------------
# Initiate (one-time)
# ---------------------------------------------------------------------------


class TestStitchInitiateOneTime:
    def test_creates_pay_by_bank_request(self) -> None:
        payment = _make_payment(PaymentType.CLASS_BOOKING, 15000)
        mock_client = MagicMock(spec=httpx.Client)
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": {
                "clientPaymentInitiationRequestCreate": {
                    "paymentInitiationRequest": {
                        "id": "pir-abc123",
                        "url": "https://secure.stitch.money/connect/payment-request/pir-abc123",
                    }
                }
            }
        }
        mock_resp.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_resp

        provider = StitchProvider(
            token_manager=_mock_token_manager(),
            http_client=mock_client,
        )
        result = provider.initiate(payment)

        assert result.provider_reference == "pir-abc123"
        assert "pir-abc123" in result.redirect_url
        assert "redirect_uri" in result.redirect_url
        # Verify GraphQL call was made
        call_args = mock_client.post.call_args
        body = call_args.kwargs.get("json") or call_args[1].get("json")
        assert "clientPaymentInitiationRequestCreate" in body["query"]
        assert body["variables"]["amount"]["quantity"] == "150.00"
        assert body["variables"]["amount"]["currency"] == "ZAR"


# ---------------------------------------------------------------------------
# Initiate (recurring / VRP)
# ---------------------------------------------------------------------------


class TestStitchInitiateRecurring:
    def test_creates_recurring_consent_for_membership(self) -> None:
        payment = _make_payment(PaymentType.MEMBERSHIP, 49900)
        mock_client = MagicMock(spec=httpx.Client)
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": {
                "paymentConsentRequestCreate": {
                    "consentRequest": {
                        "id": "consent-xyz789",
                        "url": "https://secure.stitch.money/connect/consent/consent-xyz789",
                    }
                }
            }
        }
        mock_resp.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_resp

        provider = StitchProvider(
            token_manager=_mock_token_manager(),
            http_client=mock_client,
        )
        result = provider.initiate(payment)

        assert result.provider_reference == "consent-xyz789"
        assert "consent-xyz789" in result.redirect_url
        body = mock_client.post.call_args.kwargs.get(
            "json"
        ) or mock_client.post.call_args[1].get("json")
        assert "paymentConsentRequestCreate" in body["query"]


# ---------------------------------------------------------------------------
# Svix Signature Verification
# ---------------------------------------------------------------------------


class TestSvixVerification:
    def test_valid_signature(self) -> None:
        secret = "whsec_dGVzdHNlY3JldA=="
        body = '{"event": "payment.completed"}'
        svix_id, svix_ts, svix_sig = _make_svix_signature(body, secret)

        assert verify_svix_signature(svix_id, svix_ts, svix_sig, body, secret) is True

    def test_invalid_signature(self) -> None:
        secret = "whsec_dGVzdHNlY3JldA=="
        body = '{"event": "payment.completed"}'
        assert (
            verify_svix_signature(
                "msg_1", str(int(time.time())), "v1,invalidsig", body, secret
            )
            is False
        )

    def test_expired_timestamp(self) -> None:
        secret = "whsec_dGVzdHNlY3JldA=="
        body = '{"event": "payment.completed"}'
        old_ts = str(int(time.time()) - 600)  # 10 min ago
        svix_id, _, svix_sig = _make_svix_signature(body, secret)
        # Re-sign with old timestamp
        secret_bytes = base64.b64decode(secret[6:])
        signed = f"{svix_id}.{old_ts}.{body}"
        sig = base64.b64encode(
            hmac.new(secret_bytes, signed.encode(), hashlib.sha256).digest()
        ).decode()
        assert (
            verify_svix_signature(svix_id, old_ts, f"v1,{sig}", body, secret) is False
        )

    def test_empty_secret(self) -> None:
        assert verify_svix_signature("id", "123", "v1,sig", "body", "") is False

    def test_multiple_signatures(self) -> None:
        secret = "whsec_dGVzdHNlY3JldA=="
        body = '{"data": "test"}'
        svix_id, svix_ts, svix_sig = _make_svix_signature(body, secret)
        # Prepend a bad v2 signature
        multi_sig = f"v2,badsig {svix_sig}"
        assert verify_svix_signature(svix_id, svix_ts, multi_sig, body, secret) is True


# ---------------------------------------------------------------------------
# Provider verify() method
# ---------------------------------------------------------------------------


class TestStitchProviderVerify:
    @patch("app.services.payments.stitch.settings")
    def test_verify_with_svix_fields(self, mock_settings: MagicMock) -> None:
        secret = "whsec_dGVzdHNlY3JldA=="
        mock_settings.STITCH_WEBHOOK_SECRET = secret
        mock_settings.SECRET_KEY = "fallback"

        body = '{"raw": "data"}'
        svix_id, svix_ts, svix_sig = _make_svix_signature(body, secret)

        provider = StitchProvider(token_manager=_mock_token_manager())
        result = provider.verify(
            {
                "_svix_id": svix_id,
                "_svix_timestamp": svix_ts,
                "_svix_signature": svix_sig,
                "_raw_body": body,
                "event_id": "evt-1",
                "payment_id": str(uuid4()),
                "status": "completed",
            },
            signature="ignored-when-svix-present",
        )
        assert result.is_valid is True

    @patch("app.services.payments.stitch.settings")
    def test_verify_missing_signature(self, mock_settings: MagicMock) -> None:
        provider = StitchProvider(token_manager=_mock_token_manager())
        result = provider.verify(
            {"event_id": "e1", "payment_id": "p1", "status": "completed"},
            signature=None,
        )
        assert result.is_valid is False

    @patch("app.services.payments.stitch.settings")
    def test_verify_hmac_fallback(self, mock_settings: MagicMock) -> None:
        secret = "test-webhook-secret"
        mock_settings.STITCH_WEBHOOK_SECRET = secret
        mock_settings.SECRET_KEY = "unused"

        event_id = "evt-123"
        payment_id = str(uuid4())
        status = "completed"
        expected = hmac.new(
            secret.encode(),
            f"{event_id}:{payment_id}:{status}".encode(),
            hashlib.sha256,
        ).hexdigest()

        provider = StitchProvider(token_manager=_mock_token_manager())
        result = provider.verify(
            {"event_id": event_id, "payment_id": payment_id, "status": status},
            signature=expected,
        )
        assert result.is_valid is True

    @patch("app.services.payments.stitch.settings")
    def test_verify_rejects_partial_svix_fields(self, mock_settings: MagicMock) -> None:
        mock_settings.STITCH_WEBHOOK_SECRET = "whsec_dGVzdHNlY3JldA=="
        mock_settings.SECRET_KEY = "fallback"

        provider = StitchProvider(token_manager=_mock_token_manager())
        result = provider.verify(
            {
                "event_id": "evt-1",
                "payment_id": str(uuid4()),
                "status": "completed",
                "_svix_id": "msg_123",
                "_svix_timestamp": str(int(time.time())),
            },
            signature="some-signature",
        )

        assert result.is_valid is False
        assert result.failure_reason == "missing_svix_fields"


# ---------------------------------------------------------------------------
# Refund
# ---------------------------------------------------------------------------


class TestStitchRefund:
    def test_refund_returns_success(self) -> None:
        payment = _make_payment()
        provider = StitchProvider(token_manager=_mock_token_manager())
        result = provider.refund(payment)
        assert result.is_valid is True
        assert "stitch-refund" in (result.provider_reference or "")


# ---------------------------------------------------------------------------
# GraphQL error handling
# ---------------------------------------------------------------------------


class TestStitchGraphQLErrors:
    def test_raises_on_graphql_errors(self) -> None:
        payment = _make_payment()
        mock_client = MagicMock(spec=httpx.Client)
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"errors": [{"message": "Unauthorized"}]}
        mock_resp.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_resp

        provider = StitchProvider(
            token_manager=_mock_token_manager(),
            http_client=mock_client,
        )
        with pytest.raises(RuntimeError, match="Stitch GraphQL error"):
            provider.initiate(payment)
