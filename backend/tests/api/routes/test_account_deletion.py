"""Tests for consumer account deletion endpoint (Story 1.7 - POPIA compliance).

Tests cover:
- DELETE /auth/consumer/me endpoint
- Password confirmation requirement
- Soft-delete and session invalidation
- Deleted account login prevention
- Email notification (mocked)
"""

from datetime import timedelta
from unittest.mock import patch

from sqlmodel import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models.consumer import Consumer, UserRole
from tests.utils.utils import random_email


class TestAccountDeletionEndpoint:
    """Tests for DELETE /auth/consumer/me endpoint."""

    def _create_verified_consumer(
        self, db: Session, password: str = "testpassword123"
    ) -> tuple[Consumer, str]:
        """Create a verified consumer and return with access token."""
        email = random_email()
        consumer = Consumer(
            email=email,
            first_name="Test",
            last_name="User",
            hashed_password=get_password_hash(password),
            role=UserRole.CONSUMER,
            is_email_verified=True,
            is_active=True,
            token_version=1,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)

        access_token = create_access_token(
            subject=str(consumer.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return consumer, access_token

    def test_delete_account_success(self, client, db: Session):
        """Test DELETE /me with correct password succeeds (200)."""
        password = "testpassword123"
        consumer, token = self._create_verified_consumer(db, password=password)
        original_token_version = consumer.token_version

        response = client.request(
            method="DELETE",
            url=f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"password": password},
        )

        assert response.status_code == 200
        data = response.json()
        assert "deletion" in data["message"].lower()
        assert "30 days" in data["message"].lower()

        # Verify consumer is soft-deleted
        db.refresh(consumer)
        assert consumer.is_active is False
        assert consumer.deleted_at is not None
        assert consumer.deletion_requested_at is not None
        assert consumer.token_version == original_token_version + 1

    def test_delete_account_sets_deleted_at(self, client, db: Session):
        """Test DELETE /me sets `is_active=False` and `deleted_at`."""
        password = "testpassword123"
        consumer, token = self._create_verified_consumer(db, password=password)

        # Verify initial state
        assert consumer.is_active is True
        assert consumer.deleted_at is None

        response = client.request(
            method="DELETE",
            url=f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"password": password},
        )

        assert response.status_code == 200

        # Verify soft-delete fields are set
        db.refresh(consumer)
        assert consumer.is_active is False
        assert consumer.deleted_at is not None

    def test_delete_account_sets_deletion_requested_at(self, client, db: Session):
        """Test DELETE /me sets `deletion_requested_at` timestamp."""
        password = "testpassword123"
        consumer, token = self._create_verified_consumer(db, password=password)

        # Verify initial state
        assert consumer.deletion_requested_at is None

        response = client.request(
            method="DELETE",
            url=f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"password": password},
        )

        assert response.status_code == 200

        # Verify deletion_requested_at is set
        db.refresh(consumer)
        assert consumer.deletion_requested_at is not None

    def test_delete_account_increments_token_version(self, client, db: Session):
        """Test DELETE /me increments `token_version` (invalidates tokens)."""
        password = "testpassword123"
        consumer, token = self._create_verified_consumer(db, password=password)
        original_version = consumer.token_version

        response = client.request(
            method="DELETE",
            url=f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"password": password},
        )

        assert response.status_code == 200

        # Verify token version was incremented
        db.refresh(consumer)
        assert consumer.token_version == original_version + 1

    def test_delete_account_wrong_password(self, client, db: Session):
        """Test DELETE /me with wrong password fails (401 INVALID_CREDENTIALS)."""
        password = "testpassword123"
        consumer, token = self._create_verified_consumer(db, password=password)

        response = client.request(
            method="DELETE",
            url=f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"password": "wrongpassword123"},
        )

        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"

        # Verify consumer was NOT deleted
        db.refresh(consumer)
        assert consumer.is_active is True
        assert consumer.deleted_at is None

    def test_delete_account_no_authentication(self, client):
        """Test DELETE /me without authentication fails (401)."""
        response = client.request(
            method="DELETE",
            url=f"{settings.API_V1_STR}/auth/consumer/me",
            json={"password": "testpassword123"},
        )

        assert response.status_code == 401

    def test_delete_account_invalid_token(self, client):
        """Test DELETE /me with invalid token fails (401)."""
        response = client.request(
            method="DELETE",
            url=f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": "Bearer invalid_token"},
            json={"password": "testpassword123"},
        )

        assert response.status_code == 401


class TestDeletedAccountBehavior:
    """Tests for behavior after account deletion."""

    def _create_and_delete_consumer(
        self, db: Session, password: str = "testpassword123"
    ) -> tuple[Consumer, str]:
        """Create a consumer, delete it, and return with original token."""
        email = random_email()
        consumer = Consumer(
            email=email,
            first_name="Test",
            last_name="User",
            hashed_password=get_password_hash(password),
            role=UserRole.CONSUMER,
            is_email_verified=True,
            is_active=True,
            token_version=1,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)

        # Generate token BEFORE deletion
        access_token = create_access_token(
            subject=str(consumer.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        # Delete the account
        consumer.soft_delete()
        consumer.token_version += 1
        db.commit()
        db.refresh(consumer)

        return consumer, access_token, email

    def test_deleted_consumer_cannot_login(self, client, db: Session):
        """Test deleted consumer cannot login (401 INVALID_CREDENTIALS)."""
        password = "testpassword123"
        consumer, _, email = self._create_and_delete_consumer(db, password=password)

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/login",
            json={"email": email, "password": password},
        )

        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"
        # Verify error message is generic (no enumeration)
        assert "deleted" not in response.json()["detail"]["message"].lower()

    def test_deleted_consumer_tokens_invalidated(self, client, db: Session):
        """Test deleted consumer's existing tokens are invalidated (401 on /me)."""
        password = "testpassword123"
        consumer, old_token, _ = self._create_and_delete_consumer(db, password=password)

        # Try to use the old token - should fail because consumer is inactive
        response = client.get(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {old_token}"},
        )

        assert response.status_code == 401

    def test_deleted_consumer_cannot_update_profile(self, client, db: Session):
        """Test deleted consumer cannot update profile via PATCH /me."""
        password = "testpassword123"
        consumer, old_token, _ = self._create_and_delete_consumer(db, password=password)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {old_token}"},
            json={"first_name": "NewName"},
        )

        assert response.status_code == 401


class TestAccountDeletionEmail:
    """Tests for account deletion email notification."""

    def _create_verified_consumer(
        self, db: Session, password: str = "testpassword123"
    ) -> tuple[Consumer, str]:
        """Create a verified consumer and return with access token."""
        email = random_email()
        consumer = Consumer(
            email=email,
            first_name="Test",
            last_name="User",
            hashed_password=get_password_hash(password),
            role=UserRole.CONSUMER,
            is_email_verified=True,
            is_active=True,
            token_version=1,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)

        access_token = create_access_token(
            subject=str(consumer.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return consumer, access_token

    @patch("app.api.routes.consumers.settings")
    @patch("app.api.routes.consumers.send_email")
    def test_deletion_email_sent(
        self, mock_send_email, mock_settings, client, db: Session
    ):
        """Test email is sent on successful deletion (mock)."""
        password = "testpassword123"
        consumer, token = self._create_verified_consumer(db, password=password)

        # Configure mock settings
        mock_settings.emails_enabled = True

        response = client.request(
            method="DELETE",
            url=f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"password": password},
        )

        assert response.status_code == 200

        # Verify email was called
        mock_send_email.assert_called_once()
        call_kwargs = mock_send_email.call_args[1]
        assert call_kwargs["email_to"] == consumer.email
        assert "deletion" in call_kwargs["subject"].lower()

    @patch("app.api.routes.consumers.settings")
    @patch("app.api.routes.consumers.send_email")
    def test_no_email_when_disabled(
        self, mock_send_email, mock_settings, client, db: Session
    ):
        """Test email NOT sent when emails_enabled=False."""
        password = "testpassword123"
        consumer, token = self._create_verified_consumer(db, password=password)

        # Configure mock settings
        mock_settings.emails_enabled = False

        response = client.request(
            method="DELETE",
            url=f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"password": password},
        )

        assert response.status_code == 200

        # Verify email was NOT called
        mock_send_email.assert_not_called()


class TestAccountDeletionValidation:
    """Tests for request validation."""

    def _create_verified_consumer(
        self, db: Session, password: str = "testpassword123"
    ) -> tuple[Consumer, str]:
        """Create a verified consumer and return with access token."""
        email = random_email()
        consumer = Consumer(
            email=email,
            first_name="Test",
            last_name="User",
            hashed_password=get_password_hash(password),
            role=UserRole.CONSUMER,
            is_email_verified=True,
            is_active=True,
            token_version=1,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)

        access_token = create_access_token(
            subject=str(consumer.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return consumer, access_token

    def test_delete_account_short_password(self, client, db: Session):
        """Test DELETE /me rejects password shorter than 8 characters."""
        password = "testpassword123"
        consumer, token = self._create_verified_consumer(db, password=password)

        response = client.request(
            method="DELETE",
            url=f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"password": "short"},  # Less than 8 characters
        )

        # Should fail validation
        assert response.status_code == 422

    def test_delete_account_missing_password(self, client, db: Session):
        """Test DELETE /me rejects request without password field."""
        password = "testpassword123"
        consumer, token = self._create_verified_consumer(db, password=password)

        response = client.request(
            method="DELETE",
            url=f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={},  # No password field
        )

        # Should fail validation
        assert response.status_code == 422
