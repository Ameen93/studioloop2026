"""Tests for Google OAuth login (Story 1.9).

Tests cover:
- OAuth initiation (returns redirect when configured, 503 when not)
- OAuth callback (creates new user, links existing user, handles errors)
- Set password endpoint (social-only users can add password)
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
    google_id: str | None = None,
    hashed_password: str | None = None,
    is_email_verified: bool = True,
) -> Consumer:
    """Create a test consumer."""
    consumer = Consumer(
        email=email,
        first_name="Test",
        last_name="User",
        google_id=google_id,
        hashed_password=hashed_password,
        auth_provider=AuthProvider.GOOGLE if google_id else AuthProvider.EMAIL,
        is_email_verified=is_email_verified,
        is_active=True,
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


class TestGoogleOAuthInitiation:
    """Tests for GET /auth/consumer/google endpoint."""

    def test_google_oauth_not_configured_returns_503(self, client):
        """Test returns 503 when Google OAuth is not configured."""
        with patch.object(settings, "GOOGLE_CLIENT_ID", ""):
            response = client.get(f"{settings.API_V1_STR}/auth/consumer/google")

            assert response.status_code == 503
            assert response.json()["detail"]["code"] == "OAUTH_NOT_CONFIGURED"

    def test_google_oauth_redirect_when_configured(self, client):
        """Test returns redirect when Google OAuth is configured."""
        # Skip if Google OAuth is not configured in test environment
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            pytest.skip("Google OAuth not configured in test environment")

        response = client.get(
            f"{settings.API_V1_STR}/auth/consumer/google",
            follow_redirects=False,
        )

        # Should redirect to Google
        assert response.status_code == 302
        assert "accounts.google.com" in response.headers.get("location", "")


class TestGoogleOAuthCallback:
    """Tests for GET /auth/consumer/google/callback endpoint."""

    def test_callback_not_configured_returns_503(self, client):
        """Test callback returns 503 when OAuth not configured."""
        with patch.object(settings, "GOOGLE_CLIENT_ID", ""):
            response = client.get(
                f"{settings.API_V1_STR}/auth/consumer/google/callback",
                params={"code": "test_code", "state": "test_state"},
            )

            assert response.status_code == 503
            assert response.json()["detail"]["code"] == "OAUTH_NOT_CONFIGURED"

    @patch("app.core.oauth.oauth")
    def test_callback_invalid_state_returns_400(self, mock_oauth, client):
        """Test callback returns 400 for invalid OAuth state."""
        # Mock OAuth to raise exception (invalid state)
        mock_oauth.google.authorize_access_token = AsyncMock(
            side_effect=Exception("Invalid state")
        )

        with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "GOOGLE_CLIENT_SECRET", "test_secret"):
                response = client.get(
                    f"{settings.API_V1_STR}/auth/consumer/google/callback",
                    params={"code": "test_code", "state": "invalid_state"},
                )

                assert response.status_code == 400
                assert response.json()["detail"]["code"] == "INVALID_OAUTH_STATE"

    @patch("app.core.oauth.oauth")
    def test_callback_creates_new_user(self, mock_oauth, client, db: Session):
        """Test callback creates new consumer for unknown Google ID (AC #1)."""
        google_id = f"google-{uuid4().hex[:8]}"
        email = f"newuser-{uuid4().hex[:8]}@gmail.com"

        # Mock OAuth response
        mock_oauth.google.authorize_access_token = AsyncMock(
            return_value={
                "userinfo": {
                    "sub": google_id,
                    "email": email,
                    "name": "New User",
                    "picture": "https://example.com/photo.jpg",
                }
            }
        )

        with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "GOOGLE_CLIENT_SECRET", "test_secret"):
                response = client.get(
                    f"{settings.API_V1_STR}/auth/consumer/google/callback",
                    params={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert "refresh_token" in data

                # Verify consumer was created
                consumer = db.exec(
                    select(Consumer).where(Consumer.google_id == google_id)
                ).first()
                assert consumer is not None
                assert consumer.email == email
                assert consumer.first_name == "New"
                assert consumer.last_name == "User"
                assert consumer.avatar_url == "https://example.com/photo.jpg"
                assert consumer.auth_provider == AuthProvider.GOOGLE
                assert consumer.is_email_verified is True
                assert consumer.hashed_password is None

    @patch("app.core.oauth.oauth")
    def test_callback_links_existing_email_user(self, mock_oauth, client, db: Session):
        """Test callback links Google to existing email user (AC #5)."""
        email = f"existing-{uuid4().hex[:8]}@example.com"
        google_id = f"google-{uuid4().hex[:8]}"

        # Create existing user with email login
        existing = _create_consumer(
            db,
            email=email,
            hashed_password=get_password_hash("password123"),
            is_email_verified=True,
        )
        original_id = existing.id

        # Mock OAuth response with same email
        mock_oauth.google.authorize_access_token = AsyncMock(
            return_value={
                "userinfo": {
                    "sub": google_id,
                    "email": email,
                    "name": "Test User",
                    "picture": None,
                }
            }
        )

        with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "GOOGLE_CLIENT_SECRET", "test_secret"):
                response = client.get(
                    f"{settings.API_V1_STR}/auth/consumer/google/callback",
                    params={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 200

                # Verify same consumer (not duplicated)
                db.refresh(existing)
                assert existing.id == original_id
                assert existing.google_id == google_id
                # Password should be preserved
                assert existing.hashed_password is not None

    @patch("app.core.oauth.oauth")
    def test_callback_logs_in_existing_google_user(
        self, mock_oauth, client, db: Session
    ):
        """Test callback returns tokens for existing Google user (AC #3)."""
        google_id = f"google-{uuid4().hex[:8]}"
        email = f"googleuser-{uuid4().hex[:8]}@gmail.com"

        # Create existing Google user
        existing = _create_consumer(
            db,
            email=email,
            google_id=google_id,
        )

        # Mock OAuth response
        mock_oauth.google.authorize_access_token = AsyncMock(
            return_value={
                "userinfo": {
                    "sub": google_id,
                    "email": email,
                    "name": "Test User",
                    "picture": None,
                }
            }
        )

        with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "GOOGLE_CLIENT_SECRET", "test_secret"):
                response = client.get(
                    f"{settings.API_V1_STR}/auth/consumer/google/callback",
                    params={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert "refresh_token" in data

    @patch("app.core.oauth.oauth")
    def test_callback_marks_email_verified(self, mock_oauth, client, db: Session):
        """Test callback marks email as verified (AC #1)."""
        email = f"unverified-{uuid4().hex[:8]}@example.com"
        google_id = f"google-{uuid4().hex[:8]}"

        # Create existing unverified user
        existing = _create_consumer(
            db,
            email=email,
            is_email_verified=False,
        )
        assert existing.is_email_verified is False

        # Mock OAuth response with same email
        mock_oauth.google.authorize_access_token = AsyncMock(
            return_value={
                "userinfo": {
                    "sub": google_id,
                    "email": email,
                    "name": "Test User",
                    "picture": None,
                }
            }
        )

        with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "GOOGLE_CLIENT_SECRET", "test_secret"):
                response = client.get(
                    f"{settings.API_V1_STR}/auth/consumer/google/callback",
                    params={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 200

                # Verify email is now verified
                db.refresh(existing)
                assert existing.is_email_verified is True

    @patch("app.core.oauth.oauth")
    def test_callback_imports_profile_photo(self, mock_oauth, client, db: Session):
        """Test callback imports Google profile photo (AC #2)."""
        google_id = f"google-{uuid4().hex[:8]}"
        email = f"photouser-{uuid4().hex[:8]}@gmail.com"
        photo_url = "https://lh3.googleusercontent.com/photo.jpg"

        # Mock OAuth response with picture
        mock_oauth.google.authorize_access_token = AsyncMock(
            return_value={
                "userinfo": {
                    "sub": google_id,
                    "email": email,
                    "name": "Photo User",
                    "picture": photo_url,
                }
            }
        )

        with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "GOOGLE_CLIENT_SECRET", "test_secret"):
                response = client.get(
                    f"{settings.API_V1_STR}/auth/consumer/google/callback",
                    params={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 200

                # Verify photo was imported
                consumer = db.exec(
                    select(Consumer).where(Consumer.google_id == google_id)
                ).first()
                assert consumer is not None
                assert consumer.avatar_url == photo_url

    @patch("app.core.oauth.oauth")
    def test_callback_no_email_returns_400(self, mock_oauth, client):
        """Test callback returns 400 when Google account has no email."""
        # Mock OAuth response without email
        mock_oauth.google.authorize_access_token = AsyncMock(
            return_value={
                "userinfo": {
                    "sub": "google-123",
                    "name": "No Email User",
                }
            }
        )

        with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "GOOGLE_CLIENT_SECRET", "test_secret"):
                response = client.get(
                    f"{settings.API_V1_STR}/auth/consumer/google/callback",
                    params={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 400
                assert response.json()["detail"]["code"] == "OAUTH_NO_EMAIL"

    @patch("app.core.oauth.oauth")
    def test_callback_no_userinfo_returns_400(self, mock_oauth, client):
        """Test callback returns 400 when userinfo is missing."""
        # Mock OAuth response without userinfo
        mock_oauth.google.authorize_access_token = AsyncMock(return_value={})

        with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "GOOGLE_CLIENT_SECRET", "test_secret"):
                response = client.get(
                    f"{settings.API_V1_STR}/auth/consumer/google/callback",
                    params={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 400
                assert response.json()["detail"]["code"] == "OAUTH_USER_INFO_FAILED"

    @patch("app.core.oauth.oauth")
    def test_callback_rejects_inactive_consumer(self, mock_oauth, client, db: Session):
        """Test callback rejects login for deactivated consumer."""
        email = f"inactive-{uuid4().hex[:8]}@gmail.com"
        google_id = f"google-{uuid4().hex[:8]}"

        # Create inactive (deactivated) consumer
        consumer = _create_consumer(
            db,
            email=email,
            google_id=google_id,
        )
        consumer.is_active = False
        db.add(consumer)
        db.commit()

        # Mock OAuth response for inactive user
        mock_oauth.google.authorize_access_token = AsyncMock(
            return_value={
                "userinfo": {
                    "sub": google_id,
                    "email": email,
                    "name": "Inactive User",
                    "picture": None,
                }
            }
        )

        with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
            with patch.object(settings, "GOOGLE_CLIENT_SECRET", "test_secret"):
                response = client.get(
                    f"{settings.API_V1_STR}/auth/consumer/google/callback",
                    params={"code": "test_code", "state": "valid_state"},
                )

                assert response.status_code == 403
                assert response.json()["detail"]["code"] == "ACCOUNT_DEACTIVATED"


class TestSetPassword:
    """Tests for POST /auth/consumer/set-password endpoint."""

    def test_set_password_success_for_social_user(self, client, db: Session):
        """Test social-only user can set password (AC #4)."""
        # Create social login user (no password)
        consumer = _create_consumer(
            db,
            email=f"social-{uuid4().hex[:8]}@gmail.com",
            google_id=f"google-{uuid4().hex[:8]}",
            hashed_password=None,
        )
        token = _create_consumer_token(consumer)

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/set-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"new_password": "MyNewPassword123"},
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Password has been set successfully"

        # Verify password was set
        db.refresh(consumer)
        assert consumer.hashed_password is not None

    def test_set_password_fails_when_already_set(self, client, db: Session):
        """Test returns 400 when user already has password."""
        # Create user with password
        consumer = _create_consumer(
            db,
            email=f"haspass-{uuid4().hex[:8]}@example.com",
            hashed_password=get_password_hash("existingpassword"),
        )
        token = _create_consumer_token(consumer)

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/set-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"new_password": "NewPassword123"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "PASSWORD_ALREADY_SET"

    def test_set_password_validates_minimum_length(self, client, db: Session):
        """Test password must meet minimum length requirement."""
        consumer = _create_consumer(
            db,
            email=f"shortpass-{uuid4().hex[:8]}@gmail.com",
            google_id=f"google-{uuid4().hex[:8]}",
            hashed_password=None,
        )
        token = _create_consumer_token(consumer)

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/set-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"new_password": "short"},
        )

        assert response.status_code == 422  # Validation error

    def test_set_password_requires_authentication(self, client):
        """Test endpoint requires authentication."""
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/set-password",
            json={"new_password": "MyPassword123"},
        )

        assert response.status_code == 401

    def test_social_user_can_login_after_setting_password(self, client, db: Session):
        """Test social user can use email login after setting password."""
        email = f"canlogin-{uuid4().hex[:8]}@gmail.com"
        new_password = "MyNewSecurePassword123"

        # Create social login user
        consumer = _create_consumer(
            db,
            email=email,
            google_id=f"google-{uuid4().hex[:8]}",
            hashed_password=None,
        )
        token = _create_consumer_token(consumer)

        # Set password
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/set-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"new_password": new_password},
        )
        assert response.status_code == 200

        # Now try email login
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/login",
            json={"email": email, "password": new_password},
        )

        assert response.status_code == 200
        assert "access_token" in response.json()
