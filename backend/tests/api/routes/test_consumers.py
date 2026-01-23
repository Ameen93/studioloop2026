"""Tests for consumer registration, login, and email verification endpoints.

Verifies Story 1.1 acceptance criteria:
- AC #1: Registration with email, password, first_name, last_name creates account with role: consumer
- AC #2: Password hashed with Argon2 (tested in test_security.py)
- AC #3: Verification email sent (mocked)
- AC #4: Cannot login until verified (separate test)
- AC #5: Duplicate emails rejected with EMAIL_ALREADY_EXISTS
- AC #6: UUIDs for primary keys

Verifies Story 1.2 acceptance criteria:
- AC #1: Login returns JWT access token (<24h) and refresh token
- AC #4: Invalid credentials return 401 with INVALID_CREDENTIALS
- AC #5: Unverified accounts cannot login with EMAIL_NOT_VERIFIED
"""

from unittest.mock import patch
from uuid import UUID

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import verify_password
from app.models.consumer import Consumer, UserRole
from app.utils import generate_email_verification_token
from tests.utils.utils import random_email, random_lower_string


class TestConsumerRegistration:
    """Tests for POST /auth/consumer/register endpoint."""

    def test_register_consumer_success(self, client: TestClient, db: Session) -> None:
        """Test successful consumer registration creates account with consumer role."""
        email = random_email()
        password = random_lower_string()
        data = {
            "email": email,
            "password": password,
            "first_name": "Test",
            "last_name": "User",
        }

        # Mock email sending
        with patch("app.api.routes.consumers.send_email"):
            response = client.post(
                f"{settings.API_V1_STR}/auth/consumer/register",
                json=data,
            )

        assert response.status_code == 201
        result = response.json()

        # Verify response fields
        assert result["email"] == email
        assert result["first_name"] == "Test"
        assert result["last_name"] == "User"
        assert result["role"] == "consumer"
        assert result["is_email_verified"] is False
        assert result["is_active"] is True

        # Verify UUID format (AC #6)
        assert UUID(result["id"])

        # Verify password is NOT in response
        assert "password" not in result
        assert "hashed_password" not in result

        # Verify consumer exists in database
        consumer = db.exec(select(Consumer).where(Consumer.email == email)).first()
        assert consumer is not None
        assert consumer.role == UserRole.CONSUMER
        assert verify_password(password, consumer.hashed_password)

    def test_register_consumer_sends_verification_email(
        self, client: TestClient
    ) -> None:
        """Test that registration sends verification email when enabled."""
        email = random_email()
        data = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "User",
        }

        with (
            patch("app.api.routes.consumers.send_email") as mock_send,
            patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
            patch("app.core.config.settings.EMAILS_FROM_EMAIL", "noreply@example.com"),
        ):
            response = client.post(
                f"{settings.API_V1_STR}/auth/consumer/register",
                json=data,
            )

        assert response.status_code == 201
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert call_args.kwargs["email_to"] == email

    def test_register_consumer_duplicate_email(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that duplicate email returns EMAIL_ALREADY_EXISTS error (AC #5)."""
        email = random_email()
        data = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "User",
        }

        # First registration
        with patch("app.api.routes.consumers.send_email"):
            response1 = client.post(
                f"{settings.API_V1_STR}/auth/consumer/register",
                json=data,
            )
        assert response1.status_code == 201

        # Second registration with same email
        data["password"] = random_lower_string()  # Different password
        response2 = client.post(
            f"{settings.API_V1_STR}/auth/consumer/register",
            json=data,
        )

        assert response2.status_code == 400
        result = response2.json()
        assert result["detail"]["code"] == "EMAIL_ALREADY_EXISTS"
        assert (
            result["detail"]["message"] == "An account with this email already exists"
        )
        assert result["detail"]["details"]["field"] == "email"

    def test_register_consumer_invalid_email(self, client: TestClient) -> None:
        """Test that invalid email format returns 422."""
        data = {
            "email": "not-an-email",
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "User",
        }

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/register",
            json=data,
        )

        assert response.status_code == 422

    def test_register_consumer_short_password(self, client: TestClient) -> None:
        """Test that password shorter than 8 characters returns 422."""
        data = {
            "email": random_email(),
            "password": "short",
            "first_name": "Test",
            "last_name": "User",
        }

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/register",
            json=data,
        )

        assert response.status_code == 422

    def test_register_consumer_missing_first_name(self, client: TestClient) -> None:
        """Test that missing first_name returns 422."""
        data = {
            "email": random_email(),
            "password": random_lower_string(),
            "last_name": "User",
        }

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/register",
            json=data,
        )

        assert response.status_code == 422

    def test_register_consumer_missing_last_name(self, client: TestClient) -> None:
        """Test that missing last_name returns 422."""
        data = {
            "email": random_email(),
            "password": random_lower_string(),
            "first_name": "Test",
        }

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/register",
            json=data,
        )

        assert response.status_code == 422


class TestEmailVerification:
    """Tests for GET /auth/consumer/verify-email endpoint."""

    def test_verify_email_success(self, client: TestClient, db: Session) -> None:
        """Test successful email verification sets is_email_verified to True."""
        # Create consumer first
        email = random_email()
        data = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "User",
        }

        with patch("app.api.routes.consumers.send_email"):
            client.post(
                f"{settings.API_V1_STR}/auth/consumer/register",
                json=data,
            )

        # Verify not verified yet
        consumer = db.exec(select(Consumer).where(Consumer.email == email)).first()
        assert consumer.is_email_verified is False

        # Generate verification token and verify
        token = generate_email_verification_token(email)
        response = client.get(
            f"{settings.API_V1_STR}/auth/consumer/verify-email",
            params={"token": token},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["message"] == "Email verified successfully"

        # Verify consumer is now verified
        db.refresh(consumer)
        assert consumer.is_email_verified is True

    def test_verify_email_invalid_token(self, client: TestClient) -> None:
        """Test that invalid token returns INVALID_TOKEN error."""
        response = client.get(
            f"{settings.API_V1_STR}/auth/consumer/verify-email",
            params={"token": "invalid-token"},
        )

        assert response.status_code == 400
        result = response.json()
        assert result["detail"]["code"] == "INVALID_TOKEN"

    def test_verify_email_already_verified(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that verifying an already verified email returns appropriate message."""
        # Create and verify consumer
        email = random_email()
        data = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "User",
        }

        with patch("app.api.routes.consumers.send_email"):
            client.post(
                f"{settings.API_V1_STR}/auth/consumer/register",
                json=data,
            )

        # First verification
        token = generate_email_verification_token(email)
        client.get(
            f"{settings.API_V1_STR}/auth/consumer/verify-email",
            params={"token": token},
        )

        # Second verification
        response = client.get(
            f"{settings.API_V1_STR}/auth/consumer/verify-email",
            params={"token": token},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["message"] == "Email already verified"

    def test_verify_email_consumer_not_found(self, client: TestClient) -> None:
        """Test that verifying non-existent consumer returns 404."""
        # Generate token for non-existent email
        token = generate_email_verification_token("nonexistent@example.com")
        response = client.get(
            f"{settings.API_V1_STR}/auth/consumer/verify-email",
            params={"token": token},
        )

        assert response.status_code == 404
        result = response.json()
        assert result["detail"]["code"] == "CONSUMER_NOT_FOUND"


class TestResendVerification:
    """Tests for POST /auth/consumer/resend-verification endpoint."""

    def test_resend_verification_success(self, client: TestClient, db: Session) -> None:
        """Test resending verification email."""
        email = random_email()
        data = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "User",
        }

        # Register consumer
        with patch("app.api.routes.consumers.send_email"):
            client.post(
                f"{settings.API_V1_STR}/auth/consumer/register",
                json=data,
            )

        # Resend verification
        with (
            patch("app.api.routes.consumers.send_email") as mock_send,
            patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
            patch("app.core.config.settings.EMAILS_FROM_EMAIL", "noreply@example.com"),
        ):
            response = client.post(
                f"{settings.API_V1_STR}/auth/consumer/resend-verification",
                params={"email": email},
            )

        assert response.status_code == 200
        # Email should be sent
        mock_send.assert_called_once()

    def test_resend_verification_nonexistent_email(self, client: TestClient) -> None:
        """Test resending to non-existent email returns generic message (no enumeration)."""
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/resend-verification",
            params={"email": "nonexistent@example.com"},
        )

        # Should return 200 to prevent email enumeration
        assert response.status_code == 200
        result = response.json()
        assert "verification link has been sent" in result["message"]


class TestConsumerLogin:
    """Tests for POST /auth/consumer/login endpoint.

    Story 1.2 Acceptance Criteria:
    - AC #1: Valid credentials return access_token and refresh_token
    - AC #4: Invalid credentials return 401 INVALID_CREDENTIALS
    - AC #5: Unverified accounts return 403 EMAIL_NOT_VERIFIED
    """

    def _create_verified_consumer(
        self, client: TestClient, db: Session, email: str, password: str
    ) -> Consumer:
        """Helper to create a verified consumer for testing login."""
        data = {
            "email": email,
            "password": password,
            "first_name": "Test",
            "last_name": "User",
        }

        with patch("app.api.routes.consumers.send_email"):
            client.post(
                f"{settings.API_V1_STR}/auth/consumer/register",
                json=data,
            )

        # Mark as verified
        consumer = db.exec(select(Consumer).where(Consumer.email == email)).first()
        consumer.is_email_verified = True
        db.add(consumer)
        db.commit()
        db.refresh(consumer)
        return consumer

    def test_login_success(self, client: TestClient, db: Session) -> None:
        """Test successful login returns access_token and refresh_token (AC #1)."""
        email = random_email()
        password = random_lower_string()
        self._create_verified_consumer(client, db, email, password)

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/login",
            json={"email": email, "password": password},
        )

        assert response.status_code == 200
        result = response.json()

        # Verify token response structure
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"

        # Verify tokens are non-empty strings
        assert isinstance(result["access_token"], str)
        assert len(result["access_token"]) > 0
        assert isinstance(result["refresh_token"], str)
        assert len(result["refresh_token"]) > 0

    def test_login_invalid_password(self, client: TestClient, db: Session) -> None:
        """Test login with wrong password returns 401 INVALID_CREDENTIALS (AC #4)."""
        email = random_email()
        password = random_lower_string()
        self._create_verified_consumer(client, db, email, password)

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/login",
            json={"email": email, "password": "wrongpassword"},
        )

        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_CREDENTIALS"
        assert result["detail"]["message"] == "Invalid email or password"

    def test_login_nonexistent_email(self, client: TestClient) -> None:
        """Test login with non-existent email returns 401 (same as invalid password)."""
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/login",
            json={"email": "nonexistent@example.com", "password": "anypassword123"},
        )

        # Should return same error to prevent email enumeration
        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_CREDENTIALS"

    def test_login_unverified_account(self, client: TestClient, db: Session) -> None:
        """Test login with unverified account returns 403 EMAIL_NOT_VERIFIED (AC #5)."""
        email = random_email()
        password = random_lower_string()
        data = {
            "email": email,
            "password": password,
            "first_name": "Test",
            "last_name": "User",
        }

        # Register but DON'T verify
        with patch("app.api.routes.consumers.send_email"):
            client.post(
                f"{settings.API_V1_STR}/auth/consumer/register",
                json=data,
            )

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/login",
            json={"email": email, "password": password},
        )

        assert response.status_code == 403
        result = response.json()
        assert result["detail"]["code"] == "EMAIL_NOT_VERIFIED"
        assert (
            result["detail"]["message"] == "Please verify your email before logging in"
        )
        assert result["detail"]["details"]["email"] == email

    def test_login_short_password_validation(self, client: TestClient) -> None:
        """Test login with password < 8 chars returns 422 validation error."""
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/login",
            json={"email": "test@example.com", "password": "short"},
        )

        assert response.status_code == 422

    def test_login_deactivated_account(self, client: TestClient, db: Session) -> None:
        """Test login with deactivated account returns 401 INVALID_CREDENTIALS."""
        email = random_email()
        password = random_lower_string()

        # Create and verify consumer
        self._create_verified_consumer(client, db, email, password)

        # Deactivate the consumer (soft-delete)
        consumer = db.exec(select(Consumer).where(Consumer.email == email)).first()
        consumer.is_active = False
        db.add(consumer)
        db.commit()

        # Attempt login
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/login",
            json={"email": email, "password": password},
        )

        # Should return same error as invalid credentials (no enumeration)
        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_CREDENTIALS"
