"""Tests for Apple OAuth login (Story 1.10).

Tests cover:
- OAuth initiation (returns redirect when configured, 503 when not)
- OAuth callback (creates new user, links existing user, handles errors)
- Hide My Email relay addresses support
- First-login name extraction (Apple only sends name on first auth)
"""

from datetime import timedelta
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models.consumer import AuthProvider, Consumer, UserRole


def _create_consumer(
    db: Session,
    email: str = "test@example.com",
    apple_id: str | None = None,
    google_id: str | None = None,
    hashed_password: str | None = None,
    is_email_verified: bool = True,
    is_active: bool = True,
) -> Consumer:
    """Create a test consumer."""
    auth_provider = AuthProvider.EMAIL
    if apple_id:
        auth_provider = AuthProvider.APPLE
    elif google_id:
        auth_provider = AuthProvider.GOOGLE

    consumer = Consumer(
        email=email,
        first_name="Test",
        last_name="User",
        apple_id=apple_id,
        google_id=google_id,
        hashed_password=hashed_password,
        auth_provider=auth_provider,
        is_email_verified=is_email_verified,
        is_active=is_active,
        role=UserRole.CONSUMER,
    )
    db.add(consumer)
    db.commit()
    db.refresh(consumer)
    return consumer


def _create_consumer_token(consumer: Consumer) -> str:
    """Create an access token for a consumer."""
    return create_access_token(
        subject=str(consumer.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


class TestAppleOAuthInitiation:
    """Tests for GET /auth/consumer/apple endpoint (AC #1, #4)."""

    def test_apple_oauth_not_configured_returns_503(self, client):
        """Test returns 503 when Apple OAuth is not configured."""
        with patch.object(settings, "APPLE_CLIENT_ID", ""):
            response = client.get(f"{settings.API_V1_STR}/auth/consumer/apple")

            assert response.status_code == 503
            assert response.json()["detail"]["code"] == "OAUTH_NOT_CONFIGURED"

    def test_apple_oauth_no_private_key_returns_503(self, client):
        """Test returns 503 when Apple private key is missing."""
        with patch.object(settings, "APPLE_CLIENT_ID", "com.test.app"):
            with patch.object(settings, "APPLE_PRIVATE_KEY", ""):
                response = client.get(f"{settings.API_V1_STR}/auth/consumer/apple")

                assert response.status_code == 503
                assert response.json()["detail"]["code"] == "OAUTH_NOT_CONFIGURED"

    def test_apple_oauth_redirect_when_configured(self, client):
        """Test returns redirect when Apple OAuth is configured (AC #1)."""
        # Skip if Apple OAuth is not configured in test environment
        if not settings.APPLE_CLIENT_ID or not settings.APPLE_PRIVATE_KEY:
            pytest.skip("Apple OAuth not configured in test environment")

        response = client.get(
            f"{settings.API_V1_STR}/auth/consumer/apple",
            follow_redirects=False,
        )

        # Should redirect to Apple
        assert response.status_code == 302
        assert "appleid.apple.com" in response.headers.get("location", "")


class TestAppleOAuthCallback:
    """Tests for POST /auth/consumer/apple/callback endpoint (AC #1-5)."""

    def test_callback_not_configured_returns_503(self, client):
        """Test callback returns 503 when OAuth not configured."""
        with patch.object(settings, "APPLE_CLIENT_ID", ""):
            response = client.post(
                f"{settings.API_V1_STR}/auth/consumer/apple/callback",
                data={"code": "test_code", "state": "test_state"},
            )

            assert response.status_code == 503
            assert response.json()["detail"]["code"] == "OAUTH_NOT_CONFIGURED"

    @patch("app.core.oauth.oauth")
    @patch("app.core.oauth.generate_apple_client_secret")
    def test_callback_invalid_state_returns_400(
        self, mock_gen_secret, mock_oauth, client
    ):
        """Test callback returns 400 for invalid OAuth state (AC #8)."""
        mock_gen_secret.return_value = "mock_client_secret"

        # Mock OAuth to raise exception (invalid state)
        mock_oauth.apple.authorize_access_token = AsyncMock(
            side_effect=Exception("Invalid state")
        )

        with patch.object(settings, "APPLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "APPLE_PRIVATE_KEY", "test_key"):
                response = client.post(
                    f"{settings.API_V1_STR}/auth/consumer/apple/callback",
                    data={"code": "test_code", "state": "invalid_state"},
                )

                assert response.status_code == 400
                assert response.json()["detail"]["code"] == "INVALID_OAUTH_STATE"

    @patch("app.core.oauth.oauth")
    @patch("app.core.oauth.generate_apple_client_secret")
    @patch("jwt.decode")
    def test_callback_creates_new_user(
        self, mock_jwt_decode, mock_gen_secret, mock_oauth, client, db: Session
    ):
        """Test callback creates new consumer for unknown Apple ID (AC #1, #2)."""
        apple_id = f"apple-{uuid4().hex[:8]}"
        email = f"newuser-{uuid4().hex[:8]}@privaterelay.appleid.com"

        mock_gen_secret.return_value = "mock_client_secret"

        # Mock OAuth token response
        mock_oauth.apple.authorize_access_token = AsyncMock(
            return_value={"id_token": "mock_id_token"}
        )

        # Mock JWT decode
        mock_jwt_decode.return_value = {
            "sub": apple_id,
            "email": email,
            "email_verified": "true",
        }

        # Mock form data with user info (first auth)
        user_json = '{"name": {"firstName": "John", "lastName": "Doe"}}'

        with patch.object(settings, "APPLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "APPLE_PRIVATE_KEY", "test_key"):
                response = client.post(
                    f"{settings.API_V1_STR}/auth/consumer/apple/callback",
                    data={
                        "code": "test_code",
                        "state": "valid_state",
                        "user": user_json,
                    },
                )

                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert "refresh_token" in data

                # Verify consumer was created
                consumer = db.exec(
                    select(Consumer).where(Consumer.apple_id == apple_id)
                ).first()
                assert consumer is not None
                assert consumer.email == email
                assert consumer.first_name == "John"
                assert consumer.last_name == "Doe"
                assert consumer.auth_provider == AuthProvider.APPLE
                assert consumer.is_email_verified is True
                assert consumer.hashed_password is None

    @patch("app.core.oauth.oauth")
    @patch("app.core.oauth.generate_apple_client_secret")
    @patch("jwt.decode")
    def test_callback_links_existing_email_user(
        self, mock_jwt_decode, mock_gen_secret, mock_oauth, client, db: Session
    ):
        """Test callback links Apple to existing email user (AC #5)."""
        email = f"existing-{uuid4().hex[:8]}@example.com"
        apple_id = f"apple-{uuid4().hex[:8]}"

        # Create existing user with email login
        existing = _create_consumer(
            db,
            email=email,
            hashed_password=get_password_hash("password123"),
            is_email_verified=True,
        )
        original_id = existing.id

        mock_gen_secret.return_value = "mock_client_secret"

        # Mock OAuth response
        mock_oauth.apple.authorize_access_token = AsyncMock(
            return_value={"id_token": "mock_id_token"}
        )

        mock_jwt_decode.return_value = {
            "sub": apple_id,
            "email": email,
            "email_verified": "true",
        }

        with patch.object(settings, "APPLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "APPLE_PRIVATE_KEY", "test_key"):
                response = client.post(
                    f"{settings.API_V1_STR}/auth/consumer/apple/callback",
                    data={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 200

                # Verify same consumer (not duplicated)
                db.refresh(existing)
                assert existing.id == original_id
                assert existing.apple_id == apple_id
                # Password should be preserved
                assert existing.hashed_password is not None

    @patch("app.core.oauth.oauth")
    @patch("app.core.oauth.generate_apple_client_secret")
    @patch("jwt.decode")
    def test_callback_logs_in_existing_apple_user(
        self, mock_jwt_decode, mock_gen_secret, mock_oauth, client, db: Session
    ):
        """Test callback returns tokens for existing Apple user (AC #4)."""
        apple_id = f"apple-{uuid4().hex[:8]}"
        email = f"appleuser-{uuid4().hex[:8]}@privaterelay.appleid.com"

        # Create existing Apple user
        _create_consumer(
            db,
            email=email,
            apple_id=apple_id,
        )

        mock_gen_secret.return_value = "mock_client_secret"

        # Mock OAuth response
        mock_oauth.apple.authorize_access_token = AsyncMock(
            return_value={"id_token": "mock_id_token"}
        )

        mock_jwt_decode.return_value = {
            "sub": apple_id,
            "email": email,
            "email_verified": "true",
        }

        with patch.object(settings, "APPLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "APPLE_PRIVATE_KEY", "test_key"):
                response = client.post(
                    f"{settings.API_V1_STR}/auth/consumer/apple/callback",
                    data={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert "refresh_token" in data

    @patch("app.core.oauth.oauth")
    @patch("app.core.oauth.generate_apple_client_secret")
    @patch("jwt.decode")
    def test_callback_marks_email_verified(
        self, mock_jwt_decode, mock_gen_secret, mock_oauth, client, db: Session
    ):
        """Test callback marks email as verified (AC #6)."""
        email = f"unverified-{uuid4().hex[:8]}@example.com"
        apple_id = f"apple-{uuid4().hex[:8]}"

        # Create existing unverified user
        existing = _create_consumer(
            db,
            email=email,
            is_email_verified=False,
        )
        assert existing.is_email_verified is False

        mock_gen_secret.return_value = "mock_client_secret"

        # Mock OAuth response
        mock_oauth.apple.authorize_access_token = AsyncMock(
            return_value={"id_token": "mock_id_token"}
        )

        mock_jwt_decode.return_value = {
            "sub": apple_id,
            "email": email,
            "email_verified": "true",
        }

        with patch.object(settings, "APPLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "APPLE_PRIVATE_KEY", "test_key"):
                response = client.post(
                    f"{settings.API_V1_STR}/auth/consumer/apple/callback",
                    data={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 200

                # Verify email is now verified
                db.refresh(existing)
                assert existing.is_email_verified is True

    @patch("app.core.oauth.oauth")
    @patch("app.core.oauth.generate_apple_client_secret")
    @patch("jwt.decode")
    def test_callback_accepts_hide_my_email_relay(
        self, mock_jwt_decode, mock_gen_secret, mock_oauth, client, db: Session
    ):
        """Test callback accepts Hide My Email relay addresses (AC #3, #7)."""
        apple_id = f"apple-{uuid4().hex[:8]}"
        # Apple's Hide My Email uses @privaterelay.appleid.com
        relay_email = f"abc123def{uuid4().hex[:4]}@privaterelay.appleid.com"

        mock_gen_secret.return_value = "mock_client_secret"

        # Mock OAuth response
        mock_oauth.apple.authorize_access_token = AsyncMock(
            return_value={"id_token": "mock_id_token"}
        )

        mock_jwt_decode.return_value = {
            "sub": apple_id,
            "email": relay_email,
            "email_verified": "true",
            "is_private_email": "true",
        }

        with patch.object(settings, "APPLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "APPLE_PRIVATE_KEY", "test_key"):
                response = client.post(
                    f"{settings.API_V1_STR}/auth/consumer/apple/callback",
                    data={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 200

                # Verify consumer was created with relay email
                consumer = db.exec(
                    select(Consumer).where(Consumer.apple_id == apple_id)
                ).first()
                assert consumer is not None
                assert consumer.email == relay_email
                assert "@privaterelay.appleid.com" in consumer.email

    @patch("app.core.oauth.oauth")
    @patch("app.core.oauth.generate_apple_client_secret")
    @patch("jwt.decode")
    def test_callback_no_email_returns_400(
        self, mock_jwt_decode, mock_gen_secret, mock_oauth, client
    ):
        """Test callback returns 400 when Apple account has no email."""
        mock_gen_secret.return_value = "mock_client_secret"

        # Mock OAuth response
        mock_oauth.apple.authorize_access_token = AsyncMock(
            return_value={"id_token": "mock_id_token"}
        )

        # Mock decode without email
        mock_jwt_decode.return_value = {
            "sub": "apple-123",
            # No email field
        }

        with patch.object(settings, "APPLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "APPLE_PRIVATE_KEY", "test_key"):
                response = client.post(
                    f"{settings.API_V1_STR}/auth/consumer/apple/callback",
                    data={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 400
                assert response.json()["detail"]["code"] == "OAUTH_NO_EMAIL"

    @patch("app.core.oauth.oauth")
    @patch("app.core.oauth.generate_apple_client_secret")
    def test_callback_no_id_token_returns_400(
        self, mock_gen_secret, mock_oauth, client
    ):
        """Test callback returns 400 when ID token is missing."""
        mock_gen_secret.return_value = "mock_client_secret"

        # Mock OAuth response without id_token
        mock_oauth.apple.authorize_access_token = AsyncMock(return_value={})

        with patch.object(settings, "APPLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "APPLE_PRIVATE_KEY", "test_key"):
                response = client.post(
                    f"{settings.API_V1_STR}/auth/consumer/apple/callback",
                    data={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 400
                assert response.json()["detail"]["code"] == "OAUTH_USER_INFO_FAILED"

    @patch("app.core.oauth.oauth")
    @patch("app.core.oauth.generate_apple_client_secret")
    @patch("jwt.decode")
    def test_callback_rejects_inactive_consumer(
        self, mock_jwt_decode, mock_gen_secret, mock_oauth, client, db: Session
    ):
        """Test callback rejects login for deactivated consumer (AC #9)."""
        email = f"inactive-{uuid4().hex[:8]}@privaterelay.appleid.com"
        apple_id = f"apple-{uuid4().hex[:8]}"

        # Create inactive (deactivated) consumer
        _create_consumer(
            db,
            email=email,
            apple_id=apple_id,
            is_active=False,
        )

        mock_gen_secret.return_value = "mock_client_secret"

        # Mock OAuth response
        mock_oauth.apple.authorize_access_token = AsyncMock(
            return_value={"id_token": "mock_id_token"}
        )

        mock_jwt_decode.return_value = {
            "sub": apple_id,
            "email": email,
            "email_verified": "true",
        }

        with patch.object(settings, "APPLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "APPLE_PRIVATE_KEY", "test_key"):
                response = client.post(
                    f"{settings.API_V1_STR}/auth/consumer/apple/callback",
                    data={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 403
                assert response.json()["detail"]["code"] == "ACCOUNT_DEACTIVATED"

    @patch("app.core.oauth.oauth")
    @patch("app.core.oauth.generate_apple_client_secret")
    @patch("jwt.decode")
    def test_callback_uses_default_name_without_user_data(
        self, mock_jwt_decode, mock_gen_secret, mock_oauth, client, db: Session
    ):
        """Test callback uses default name when user data is not provided (subsequent logins)."""
        apple_id = f"apple-{uuid4().hex[:8]}"
        email = f"noname-{uuid4().hex[:8]}@privaterelay.appleid.com"

        mock_gen_secret.return_value = "mock_client_secret"

        # Mock OAuth response
        mock_oauth.apple.authorize_access_token = AsyncMock(
            return_value={"id_token": "mock_id_token"}
        )

        mock_jwt_decode.return_value = {
            "sub": apple_id,
            "email": email,
            "email_verified": "true",
        }

        with patch.object(settings, "APPLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "APPLE_PRIVATE_KEY", "test_key"):
                # No "user" field in form data (subsequent login)
                response = client.post(
                    f"{settings.API_V1_STR}/auth/consumer/apple/callback",
                    data={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 200

                # Verify default name was used
                consumer = db.exec(
                    select(Consumer).where(Consumer.apple_id == apple_id)
                ).first()
                assert consumer is not None
                assert consumer.first_name == "Apple"
                assert consumer.last_name == "User"

    @patch("app.core.oauth.oauth")
    @patch("app.core.oauth.generate_apple_client_secret")
    @patch("jwt.decode")
    def test_callback_handles_malformed_user_data(
        self, mock_jwt_decode, mock_gen_secret, mock_oauth, client, db: Session
    ):
        """Test callback handles malformed user JSON gracefully."""
        apple_id = f"apple-{uuid4().hex[:8]}"
        email = f"malformed-{uuid4().hex[:8]}@privaterelay.appleid.com"

        mock_gen_secret.return_value = "mock_client_secret"

        # Mock OAuth response
        mock_oauth.apple.authorize_access_token = AsyncMock(
            return_value={"id_token": "mock_id_token"}
        )

        mock_jwt_decode.return_value = {
            "sub": apple_id,
            "email": email,
            "email_verified": "true",
        }

        with patch.object(settings, "APPLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "APPLE_PRIVATE_KEY", "test_key"):
                # Malformed JSON in user field
                response = client.post(
                    f"{settings.API_V1_STR}/auth/consumer/apple/callback",
                    data={
                        "code": "test_code",
                        "state": "valid_state",
                        "user": "not valid json",
                    },
                )

                assert response.status_code == 200

                # Should use default name
                consumer = db.exec(
                    select(Consumer).where(Consumer.apple_id == apple_id)
                ).first()
                assert consumer is not None
                assert consumer.first_name == "Apple"
                assert consumer.last_name == "User"

    @patch("app.core.oauth.oauth")
    @patch("app.core.oauth.generate_apple_client_secret")
    @patch("jwt.decode")
    def test_callback_jwt_decode_error_returns_400(
        self, mock_jwt_decode, mock_gen_secret, mock_oauth, client
    ):
        """Test callback returns 400 when JWT decode fails."""
        mock_gen_secret.return_value = "mock_client_secret"

        # Mock OAuth response
        mock_oauth.apple.authorize_access_token = AsyncMock(
            return_value={"id_token": "mock_id_token"}
        )

        # Mock decode to raise exception
        mock_jwt_decode.side_effect = Exception("Invalid JWT")

        with patch.object(settings, "APPLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "APPLE_PRIVATE_KEY", "test_key"):
                response = client.post(
                    f"{settings.API_V1_STR}/auth/consumer/apple/callback",
                    data={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 400
                assert response.json()["detail"]["code"] == "OAUTH_USER_INFO_FAILED"
