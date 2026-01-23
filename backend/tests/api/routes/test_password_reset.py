"""Tests for password reset endpoints (Story 1.5).

Tests cover:
- Consumer forgot-password (AC #1, #5)
- Consumer reset-password (AC #2, #3, #4)
- Staff forgot-password (AC #1, #5)
- Staff reset-password (AC #2, #3, #4)
- Session invalidation via token_version
- No enumeration attacks (same response for valid/invalid emails)
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.security import ALGORITHM, get_password_hash, verify_password
from app.models import Gym
from app.models.consumer import Consumer, UserRole
from app.models.staff import Staff, StaffRole
from app.utils import generate_password_reset_token
from tests.utils.utils import random_email, random_lower_string


class TestConsumerForgotPassword:
    """Tests for POST /auth/consumer/forgot-password endpoint."""

    def _create_verified_consumer(
        self, db: Session, email: str, password: str
    ) -> Consumer:
        """Helper to create a verified consumer."""
        consumer = Consumer(
            email=email,
            first_name="Test",
            last_name="Consumer",
            hashed_password=get_password_hash(password),
            is_email_verified=True,
            is_active=True,
            token_version=1,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)
        return consumer

    def _create_unverified_consumer(self, db: Session, email: str) -> Consumer:
        """Helper to create an unverified consumer."""
        consumer = Consumer(
            email=email,
            first_name="Unverified",
            last_name="Consumer",
            hashed_password=get_password_hash("password123"),
            is_email_verified=False,
            is_active=True,
            token_version=1,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)
        return consumer

    def _create_inactive_consumer(self, db: Session, email: str) -> Consumer:
        """Helper to create an inactive consumer."""
        consumer = Consumer(
            email=email,
            first_name="Inactive",
            last_name="Consumer",
            hashed_password=get_password_hash("password123"),
            is_email_verified=True,
            is_active=False,
            token_version=1,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)
        return consumer

    def test_forgot_password_valid_email(self, client: TestClient, db: Session) -> None:
        """Test forgot-password returns success for valid email (AC #1)."""
        email = random_email()
        self._create_verified_consumer(db, email, "password123")

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/forgot-password",
            json={"email": email},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "If the email exists, a password reset link has been sent"

    def test_forgot_password_invalid_email_no_enumeration(
        self, client: TestClient
    ) -> None:
        """Test forgot-password returns same success for invalid email (AC #5)."""
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/forgot-password",
            json={"email": "nonexistent@test.com"},
        )

        # Must return SAME response to prevent enumeration
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "If the email exists, a password reset link has been sent"

    def test_forgot_password_unverified_email_no_email_sent(
        self, client: TestClient, db: Session
    ) -> None:
        """Test forgot-password doesn't send email for unverified account."""
        email = random_email()
        self._create_unverified_consumer(db, email)

        with patch("app.api.routes.consumers.send_email") as mock_send:
            response = client.post(
                f"{settings.API_V1_STR}/auth/consumer/forgot-password",
                json={"email": email},
            )

            # Should return success but NOT send email
            assert response.status_code == 200
            mock_send.assert_not_called()

    def test_forgot_password_inactive_account_no_email_sent(
        self, client: TestClient, db: Session
    ) -> None:
        """Test forgot-password doesn't send email for inactive account."""
        email = random_email()
        self._create_inactive_consumer(db, email)

        with patch("app.api.routes.consumers.send_email") as mock_send:
            response = client.post(
                f"{settings.API_V1_STR}/auth/consumer/forgot-password",
                json={"email": email},
            )

            # Should return success but NOT send email
            assert response.status_code == 200
            mock_send.assert_not_called()


class TestConsumerResetPassword:
    """Tests for POST /auth/consumer/reset-password endpoint."""

    def _create_verified_consumer(
        self, db: Session, email: str, password: str
    ) -> Consumer:
        """Helper to create a verified consumer."""
        consumer = Consumer(
            email=email,
            first_name="Test",
            last_name="Consumer",
            hashed_password=get_password_hash(password),
            is_email_verified=True,
            is_active=True,
            token_version=1,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)
        return consumer

    def _create_inactive_consumer(self, db: Session, email: str) -> Consumer:
        """Helper to create an inactive consumer."""
        consumer = Consumer(
            email=email,
            first_name="Inactive",
            last_name="Consumer",
            hashed_password=get_password_hash("password123"),
            is_email_verified=True,
            is_active=False,
            token_version=1,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)
        return consumer

    def test_reset_password_success(self, client: TestClient, db: Session) -> None:
        """Test reset-password updates password successfully (AC #3)."""
        email = random_email()
        consumer = self._create_verified_consumer(db, email, "oldpassword123")

        # Generate valid reset token
        token = generate_password_reset_token(email, account_type="consumer")

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/reset-password",
            json={"token": token, "new_password": "newpassword123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password has been reset successfully"

        # Verify password was updated
        db.refresh(consumer)
        assert verify_password("newpassword123", consumer.hashed_password)

    def test_reset_password_invalidates_sessions(
        self, client: TestClient, db: Session
    ) -> None:
        """Test reset-password increments token_version (AC #4)."""
        email = random_email()
        consumer = self._create_verified_consumer(db, email, "oldpassword123")
        original_version = consumer.token_version

        token = generate_password_reset_token(email, account_type="consumer")

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/reset-password",
            json={"token": token, "new_password": "newpassword123"},
        )

        assert response.status_code == 200

        # Verify token_version was incremented
        db.refresh(consumer)
        assert consumer.token_version == original_version + 1

    def test_reset_password_old_refresh_token_fails(
        self, client: TestClient, db: Session
    ) -> None:
        """Test old refresh tokens fail after password reset (AC #4)."""
        email = random_email()
        password = "oldpassword123"
        self._create_verified_consumer(db, email, password)

        # Login to get refresh token
        login_response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/login",
            json={"email": email, "password": password},
        )
        assert login_response.status_code == 200
        old_refresh_token = login_response.json()["refresh_token"]

        # Reset password
        reset_token = generate_password_reset_token(email, account_type="consumer")
        reset_response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/reset-password",
            json={"token": reset_token, "new_password": "newpassword123"},
        )
        assert reset_response.status_code == 200

        # Try to use old refresh token - should fail
        refresh_response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/refresh",
            json={"refresh_token": old_refresh_token},
        )
        assert refresh_response.status_code == 401
        assert refresh_response.json()["detail"]["code"] == "INVALID_TOKEN"

    def test_reset_password_can_login_with_new_password(
        self, client: TestClient, db: Session
    ) -> None:
        """Test can login with new password after reset."""
        email = random_email()
        self._create_verified_consumer(db, email, "oldpassword123")

        token = generate_password_reset_token(email, account_type="consumer")

        # Reset password
        reset_response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/reset-password",
            json={"token": token, "new_password": "newpassword123"},
        )
        assert reset_response.status_code == 200

        # Login with new password
        login_response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/login",
            json={"email": email, "password": "newpassword123"},
        )
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

    def test_reset_password_expired_token(self, client: TestClient) -> None:
        """Test reset-password with expired token returns 400."""
        # Create an expired token
        expire = datetime.now(timezone.utc) - timedelta(hours=1)
        expired_token = jwt.encode(
            {"exp": expire.timestamp(), "nbf": datetime.now(timezone.utc), "sub": "test@test.com"},
            settings.SECRET_KEY,
            algorithm=ALGORITHM,
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/reset-password",
            json={"token": expired_token, "new_password": "newpassword123"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"

    def test_reset_password_invalid_token(self, client: TestClient) -> None:
        """Test reset-password with invalid token returns 400."""
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/reset-password",
            json={"token": "invalid-random-string", "new_password": "newpassword123"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"

    def test_reset_password_nonexistent_user(self, client: TestClient) -> None:
        """Test reset-password for nonexistent user returns same error."""
        # Generate token for email that doesn't exist
        token = generate_password_reset_token("nonexistent@test.com", account_type="consumer")

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/reset-password",
            json={"token": token, "new_password": "newpassword123"},
        )

        # Should return same error to prevent enumeration
        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"

    def test_reset_password_inactive_user(self, client: TestClient, db: Session) -> None:
        """Test reset-password for inactive user returns same error."""
        email = random_email()
        self._create_inactive_consumer(db, email)

        token = generate_password_reset_token(email, account_type="consumer")

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/reset-password",
            json={"token": token, "new_password": "newpassword123"},
        )

        # Should return same error to prevent enumeration
        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"

    def test_reset_password_too_short(self, client: TestClient, db: Session) -> None:
        """Test reset-password with password too short returns validation error."""
        email = random_email()
        self._create_verified_consumer(db, email, "oldpassword123")

        token = generate_password_reset_token(email, account_type="consumer")

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/reset-password",
            json={"token": token, "new_password": "short"},
        )

        assert response.status_code == 422  # Validation error


class TestStaffForgotPassword:
    """Tests for POST /auth/staff/forgot-password endpoint."""

    def _get_test_gym(self, db: Session) -> Gym:
        """Get first gym from seeded data."""
        from sqlmodel import select

        gym = db.exec(select(Gym)).first()
        if not gym:
            raise RuntimeError("No seeded gym found")
        return gym

    def _create_active_staff(
        self, db: Session, email: str, password: str, gym_id
    ) -> Staff:
        """Helper to create an active staff member."""
        staff = Staff(
            email=email,
            first_name="Test",
            last_name="Staff",
            hashed_password=get_password_hash(password),
            role=StaffRole.MANAGER,
            gym_id=gym_id,
            is_active=True,
            token_version=1,
        )
        db.add(staff)
        db.commit()
        db.refresh(staff)
        return staff

    def _create_inactive_staff(self, db: Session, email: str, gym_id) -> Staff:
        """Helper to create an inactive staff member."""
        staff = Staff(
            email=email,
            first_name="Inactive",
            last_name="Staff",
            hashed_password=get_password_hash("password123"),
            role=StaffRole.FRONT_DESK,
            gym_id=gym_id,
            is_active=False,
            token_version=1,
        )
        db.add(staff)
        db.commit()
        db.refresh(staff)
        return staff

    def test_forgot_password_valid_email(self, client: TestClient, db: Session) -> None:
        """Test staff forgot-password returns success for valid email."""
        gym = self._get_test_gym(db)
        email = random_email()
        self._create_active_staff(db, email, "password123", gym.id)

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/forgot-password",
            json={"email": email},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "If the email exists, a password reset link has been sent"

    def test_forgot_password_invalid_email_no_enumeration(
        self, client: TestClient
    ) -> None:
        """Test staff forgot-password returns same success for invalid email."""
        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/forgot-password",
            json={"email": "nonexistent-staff@test.com"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "If the email exists, a password reset link has been sent"

    def test_forgot_password_inactive_no_email_sent(
        self, client: TestClient, db: Session
    ) -> None:
        """Test staff forgot-password doesn't send email for inactive staff."""
        gym = self._get_test_gym(db)
        email = random_email()
        self._create_inactive_staff(db, email, gym.id)

        with patch("app.api.routes.staff_auth.send_email") as mock_send:
            response = client.post(
                f"{settings.API_V1_STR}/auth/staff/forgot-password",
                json={"email": email},
            )

            assert response.status_code == 200
            mock_send.assert_not_called()


class TestStaffResetPassword:
    """Tests for POST /auth/staff/reset-password endpoint."""

    def _get_test_gym(self, db: Session) -> Gym:
        """Get first gym from seeded data."""
        from sqlmodel import select

        gym = db.exec(select(Gym)).first()
        if not gym:
            raise RuntimeError("No seeded gym found")
        return gym

    def _create_active_staff(
        self, db: Session, email: str, password: str, gym_id
    ) -> Staff:
        """Helper to create an active staff member."""
        staff = Staff(
            email=email,
            first_name="Test",
            last_name="Staff",
            hashed_password=get_password_hash(password),
            role=StaffRole.MANAGER,
            gym_id=gym_id,
            is_active=True,
            token_version=1,
        )
        db.add(staff)
        db.commit()
        db.refresh(staff)
        return staff

    def _create_inactive_staff(self, db: Session, email: str, gym_id) -> Staff:
        """Helper to create an inactive staff member."""
        staff = Staff(
            email=email,
            first_name="Inactive",
            last_name="Staff",
            hashed_password=get_password_hash("password123"),
            role=StaffRole.FRONT_DESK,
            gym_id=gym_id,
            is_active=False,
            token_version=1,
        )
        db.add(staff)
        db.commit()
        db.refresh(staff)
        return staff

    def test_reset_password_success(self, client: TestClient, db: Session) -> None:
        """Test staff reset-password updates password successfully."""
        gym = self._get_test_gym(db)
        email = random_email()
        staff = self._create_active_staff(db, email, "oldpassword123", gym.id)

        token = generate_password_reset_token(email, account_type="staff")

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/reset-password",
            json={"token": token, "new_password": "newpassword123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password has been reset successfully"

        # Verify password was updated
        db.refresh(staff)
        assert verify_password("newpassword123", staff.hashed_password)

    def test_reset_password_invalidates_sessions(
        self, client: TestClient, db: Session
    ) -> None:
        """Test staff reset-password increments token_version."""
        gym = self._get_test_gym(db)
        email = random_email()
        staff = self._create_active_staff(db, email, "oldpassword123", gym.id)
        original_version = staff.token_version

        token = generate_password_reset_token(email, account_type="staff")

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/reset-password",
            json={"token": token, "new_password": "newpassword123"},
        )

        assert response.status_code == 200

        # Verify token_version was incremented
        db.refresh(staff)
        assert staff.token_version == original_version + 1

    def test_reset_password_preserves_role_after_login(
        self, client: TestClient, db: Session
    ) -> None:
        """Test staff role is preserved after password reset and re-login."""
        gym = self._get_test_gym(db)
        email = random_email()
        staff = self._create_active_staff(db, email, "oldpassword123", gym.id)
        original_role = staff.role.value

        token = generate_password_reset_token(email, account_type="staff")

        # Reset password
        reset_response = client.post(
            f"{settings.API_V1_STR}/auth/staff/reset-password",
            json={"token": token, "new_password": "newpassword123"},
        )
        assert reset_response.status_code == 200

        # Login with new password
        login_response = client.post(
            f"{settings.API_V1_STR}/auth/staff/login",
            json={"email": email, "password": "newpassword123"},
        )
        assert login_response.status_code == 200

        # Verify role is preserved
        login_data = login_response.json()
        assert login_data["role"] == original_role

    def test_reset_password_old_refresh_token_fails(
        self, client: TestClient, db: Session
    ) -> None:
        """Test old staff refresh tokens fail after password reset."""
        gym = self._get_test_gym(db)
        email = random_email()
        password = "oldpassword123"
        self._create_active_staff(db, email, password, gym.id)

        # Login to get refresh token
        login_response = client.post(
            f"{settings.API_V1_STR}/auth/staff/login",
            json={"email": email, "password": password},
        )
        assert login_response.status_code == 200
        old_refresh_token = login_response.json()["refresh_token"]

        # Reset password
        reset_token = generate_password_reset_token(email, account_type="staff")
        reset_response = client.post(
            f"{settings.API_V1_STR}/auth/staff/reset-password",
            json={"token": reset_token, "new_password": "newpassword123"},
        )
        assert reset_response.status_code == 200

        # Try to use old refresh token - should fail
        refresh_response = client.post(
            f"{settings.API_V1_STR}/auth/staff/refresh",
            json={"refresh_token": old_refresh_token},
        )
        assert refresh_response.status_code == 401
        assert refresh_response.json()["detail"]["code"] == "INVALID_TOKEN"

    def test_reset_password_invalid_token(self, client: TestClient) -> None:
        """Test staff reset-password with invalid token returns 400."""
        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/reset-password",
            json={"token": "invalid-token", "new_password": "newpassword123"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"

    def test_reset_password_inactive_user(
        self, client: TestClient, db: Session
    ) -> None:
        """Test staff reset-password for inactive staff returns same error."""
        gym = self._get_test_gym(db)
        email = random_email()
        self._create_inactive_staff(db, email, gym.id)

        token = generate_password_reset_token(email, account_type="staff")

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/reset-password",
            json={"token": token, "new_password": "newpassword123"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"


class TestCrossAccountResetRejection:
    """Security tests for cross-account reset token rejection.

    These tests verify that reset tokens are scoped to account type,
    preventing a token generated for one account type from being used
    to reset a password on a different account type.
    """

    def _get_test_gym(self, db: Session) -> Gym:
        """Get first gym from seeded data."""
        from sqlmodel import select

        gym = db.exec(select(Gym)).first()
        if not gym:
            raise RuntimeError("No seeded gym found")
        return gym

    def _create_verified_consumer(
        self, db: Session, email: str, password: str
    ) -> Consumer:
        """Helper to create a verified consumer."""
        consumer = Consumer(
            email=email,
            first_name="Test",
            last_name="Consumer",
            hashed_password=get_password_hash(password),
            is_email_verified=True,
            is_active=True,
            token_version=1,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)
        return consumer

    def _create_active_staff(
        self, db: Session, email: str, password: str, gym_id
    ) -> Staff:
        """Helper to create an active staff member."""
        staff = Staff(
            email=email,
            first_name="Test",
            last_name="Staff",
            hashed_password=get_password_hash(password),
            role=StaffRole.MANAGER,
            gym_id=gym_id,
            is_active=True,
            token_version=1,
        )
        db.add(staff)
        db.commit()
        db.refresh(staff)
        return staff

    def test_consumer_token_cannot_reset_staff_password(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that a consumer reset token cannot be used on staff endpoint.

        This is a critical security test to prevent cross-account password resets
        when the same email exists in both consumer and staff tables.
        """
        gym = self._get_test_gym(db)
        email = random_email()

        # Create both a consumer and staff with the same email
        self._create_verified_consumer(db, email, "consumer_password")
        staff = self._create_active_staff(db, email, "staff_password", gym.id)

        # Generate a consumer reset token
        consumer_token = generate_password_reset_token(email, account_type="consumer")

        # Try to use the consumer token on the staff endpoint - should fail
        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/reset-password",
            json={"token": consumer_token, "new_password": "hacked_password"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"

        # Verify staff password was NOT changed
        db.refresh(staff)
        assert verify_password("staff_password", staff.hashed_password)

    def test_staff_token_cannot_reset_consumer_password(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that a staff reset token cannot be used on consumer endpoint.

        This is a critical security test to prevent cross-account password resets
        when the same email exists in both consumer and staff tables.
        """
        gym = self._get_test_gym(db)
        email = random_email()

        # Create both a consumer and staff with the same email
        consumer = self._create_verified_consumer(db, email, "consumer_password")
        self._create_active_staff(db, email, "staff_password", gym.id)

        # Generate a staff reset token
        staff_token = generate_password_reset_token(email, account_type="staff")

        # Try to use the staff token on the consumer endpoint - should fail
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/reset-password",
            json={"token": staff_token, "new_password": "hacked_password"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"

        # Verify consumer password was NOT changed
        db.refresh(consumer)
        assert verify_password("consumer_password", consumer.hashed_password)

    def test_user_token_cannot_reset_consumer_password(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that an admin/user reset token cannot be used on consumer endpoint."""
        email = random_email()
        consumer = self._create_verified_consumer(db, email, "consumer_password")

        # Generate a user (admin) reset token
        user_token = generate_password_reset_token(email, account_type="user")

        # Try to use the user token on the consumer endpoint - should fail
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/reset-password",
            json={"token": user_token, "new_password": "hacked_password"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"

        # Verify consumer password was NOT changed
        db.refresh(consumer)
        assert verify_password("consumer_password", consumer.hashed_password)

    def test_user_token_cannot_reset_staff_password(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that an admin/user reset token cannot be used on staff endpoint."""
        gym = self._get_test_gym(db)
        email = random_email()
        staff = self._create_active_staff(db, email, "staff_password", gym.id)

        # Generate a user (admin) reset token
        user_token = generate_password_reset_token(email, account_type="user")

        # Try to use the user token on the staff endpoint - should fail
        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/reset-password",
            json={"token": user_token, "new_password": "hacked_password"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"

        # Verify staff password was NOT changed
        db.refresh(staff)
        assert verify_password("staff_password", staff.hashed_password)
