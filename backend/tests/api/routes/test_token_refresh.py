"""Tests for token refresh endpoints.

Verifies Story 1.4 acceptance criteria:
- AC #1: App requests new access token using refresh token
- AC #2: Old refresh token is invalidated (rotation via token_version)
- AC #3: New refresh token is issued
- AC #4: Invalid/expired refresh token returns 401
"""

import uuid
from datetime import timedelta

import jwt
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
)
from app.models import Gym
from app.models.consumer import Consumer, UserRole
from app.models.staff import Staff, StaffRole
from tests.utils.utils import random_email, random_lower_string


class TestConsumerTokenRefresh:
    """Tests for POST /auth/consumer/refresh endpoint."""

    def _create_verified_consumer(
        self,
        db: Session,
        email: str,
        password: str,
        is_active: bool = True,
    ) -> Consumer:
        """Helper to create a verified consumer for testing."""
        consumer = Consumer(
            email=email,
            hashed_password=get_password_hash(password),
            first_name="Test",
            last_name="Consumer",
            role=UserRole.CONSUMER,
            is_active=is_active,
            is_email_verified=True,
            token_version=1,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)
        return consumer

    def test_consumer_refresh_success(self, client: TestClient, db: Session) -> None:
        """Test successful consumer token refresh returns new token pair (AC #1, #3)."""
        email = random_email()
        password = random_lower_string()
        consumer = self._create_verified_consumer(db, email, password)

        # Generate a valid refresh token with token_version
        refresh_token = create_refresh_token(
            subject=str(consumer.id),
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            token_version=consumer.token_version,
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        result = response.json()

        # Verify response structure
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"

        # Verify tokens are non-empty
        assert len(result["access_token"]) > 0
        assert len(result["refresh_token"]) > 0

    def test_consumer_refresh_increments_token_version(
        self, client: TestClient, db: Session
    ) -> None:
        """Test refresh increments token_version (rotation - AC #2)."""
        email = random_email()
        password = random_lower_string()
        consumer = self._create_verified_consumer(db, email, password)
        original_version = consumer.token_version

        # Generate refresh token with current version
        refresh_token = create_refresh_token(
            subject=str(consumer.id),
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            token_version=consumer.token_version,
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200

        # Refresh consumer from DB and check version incremented
        db.refresh(consumer)
        assert consumer.token_version == original_version + 1

        # New refresh token should have updated version
        result = response.json()
        payload = jwt.decode(
            result["refresh_token"],
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )
        assert payload["token_version"] == original_version + 1

    def test_consumer_refresh_old_token_rejected_after_rotation(
        self, client: TestClient, db: Session
    ) -> None:
        """Test old refresh token is rejected after rotation (AC #2)."""
        email = random_email()
        password = random_lower_string()
        consumer = self._create_verified_consumer(db, email, password)

        # Generate first refresh token
        first_token = create_refresh_token(
            subject=str(consumer.id),
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            token_version=consumer.token_version,
        )

        # Use first token to refresh (this increments version)
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/refresh",
            json={"refresh_token": first_token},
        )
        assert response.status_code == 200

        # Try to use the same token again - should fail
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/refresh",
            json={"refresh_token": first_token},
        )

        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_TOKEN"

    def test_consumer_refresh_new_access_token_is_valid(
        self, client: TestClient, db: Session
    ) -> None:
        """Test new access token can be decoded and has correct claims."""
        email = random_email()
        password = random_lower_string()
        consumer = self._create_verified_consumer(db, email, password)

        refresh_token = create_refresh_token(
            subject=str(consumer.id),
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            token_version=consumer.token_version,
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        result = response.json()

        # Decode and verify new access token
        payload = jwt.decode(
            result["access_token"],
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )

        assert payload["sub"] == str(consumer.id)
        assert payload["type"] == "access"

    def test_consumer_refresh_expired_token(
        self, client: TestClient, db: Session
    ) -> None:
        """Test expired refresh token returns 401 (AC #4)."""
        email = random_email()
        password = random_lower_string()
        consumer = self._create_verified_consumer(db, email, password)

        # Create an expired token (negative expiry)
        expired_token = create_refresh_token(
            subject=str(consumer.id),
            expires_delta=timedelta(seconds=-10),
            token_version=consumer.token_version,
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/refresh",
            json={"refresh_token": expired_token},
        )

        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_TOKEN"
        assert result["detail"]["message"] == "Invalid or expired refresh token"

    def test_consumer_refresh_access_token_rejected(
        self, client: TestClient, db: Session
    ) -> None:
        """Test access token in refresh endpoint returns 401 (wrong type - AC #4)."""
        email = random_email()
        password = random_lower_string()
        consumer = self._create_verified_consumer(db, email, password)

        # Use access token instead of refresh token
        access_token = create_access_token(
            subject=str(consumer.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/refresh",
            json={"refresh_token": access_token},
        )

        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_TOKEN"

    def test_consumer_refresh_invalid_token(self, client: TestClient) -> None:
        """Test malformed token returns 401 (AC #4)."""
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/refresh",
            json={"refresh_token": "not.a.valid.token"},
        )

        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_TOKEN"

    def test_consumer_refresh_inactive_user(
        self, client: TestClient, db: Session
    ) -> None:
        """Test inactive user's refresh token returns 401 (AC #4)."""
        email = random_email()
        password = random_lower_string()
        consumer = self._create_verified_consumer(db, email, password, is_active=False)

        refresh_token = create_refresh_token(
            subject=str(consumer.id),
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            token_version=consumer.token_version,
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_TOKEN"

    def test_consumer_refresh_nonexistent_user(self, client: TestClient) -> None:
        """Test token for deleted user returns 401 (AC #4)."""
        # Create token with non-existent user ID
        refresh_token = create_refresh_token(
            subject=str(uuid.uuid4()),
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            token_version=1,
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_TOKEN"

    def test_consumer_refresh_wrong_version_rejected(
        self, client: TestClient, db: Session
    ) -> None:
        """Test refresh token with wrong version returns 401 (AC #2)."""
        email = random_email()
        password = random_lower_string()
        consumer = self._create_verified_consumer(db, email, password)

        # Create token with wrong version (higher than current)
        wrong_version_token = create_refresh_token(
            subject=str(consumer.id),
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            token_version=consumer.token_version + 10,  # Wrong version
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/refresh",
            json={"refresh_token": wrong_version_token},
        )

        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_TOKEN"


class TestStaffTokenRefresh:
    """Tests for POST /auth/staff/refresh endpoint."""

    def _get_gym(self, db: Session) -> Gym:
        """Get an existing seed gym for testing."""
        gym = db.exec(select(Gym)).first()
        assert gym is not None, "Seed gym should exist (seeded in conftest.py)"
        return gym

    def _create_staff(
        self,
        db: Session,
        gym_id: str,
        email: str,
        password: str,
        role: StaffRole = StaffRole.OWNER,
        is_active: bool = True,
    ) -> Staff:
        """Helper to create a staff member for testing."""
        staff = Staff(
            gym_id=gym_id,
            email=email,
            hashed_password=get_password_hash(password),
            first_name="Test",
            last_name="Staff",
            role=role,
            is_active=is_active,
            token_version=1,
        )
        db.add(staff)
        db.commit()
        db.refresh(staff)
        return staff

    def test_staff_refresh_success(self, client: TestClient, db: Session) -> None:
        """Test successful staff token refresh returns new token pair (AC #1, #3)."""
        gym = self._get_gym(db)
        email = random_email()
        password = random_lower_string()
        staff = self._create_staff(db, str(gym.id), email, password, StaffRole.OWNER)

        refresh_token = create_refresh_token(
            subject=str(staff.id),
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            role=staff.role.value,
            gym_id=str(staff.gym_id),
            token_version=staff.token_version,
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        result = response.json()

        # Verify response structure
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert "role" in result
        assert "gym_id" in result

    def test_staff_refresh_old_token_rejected_after_rotation(
        self, client: TestClient, db: Session
    ) -> None:
        """Test old staff refresh token is rejected after rotation (AC #2)."""
        gym = self._get_gym(db)
        email = random_email()
        password = random_lower_string()
        staff = self._create_staff(db, str(gym.id), email, password)

        # Generate first refresh token
        first_token = create_refresh_token(
            subject=str(staff.id),
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            role=staff.role.value,
            gym_id=str(staff.gym_id),
            token_version=staff.token_version,
        )

        # Use first token to refresh (this increments version)
        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/refresh",
            json={"refresh_token": first_token},
        )
        assert response.status_code == 200

        # Try to use the same token again - should fail
        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/refresh",
            json={"refresh_token": first_token},
        )

        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_TOKEN"

    def test_staff_refresh_preserves_role(
        self, client: TestClient, db: Session
    ) -> None:
        """Test new access token has same role claim (AC #1)."""
        gym = self._get_gym(db)
        email = random_email()
        password = random_lower_string()
        staff = self._create_staff(db, str(gym.id), email, password, StaffRole.MANAGER)

        refresh_token = create_refresh_token(
            subject=str(staff.id),
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            role=staff.role.value,
            gym_id=str(staff.gym_id),
            token_version=staff.token_version,
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        result = response.json()

        # Verify role is preserved
        assert result["role"] == "manager"

        # Also verify in the access token payload
        payload = jwt.decode(
            result["access_token"],
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )
        assert payload["role"] == "manager"

    def test_staff_refresh_preserves_gym_id(
        self, client: TestClient, db: Session
    ) -> None:
        """Test new access token has same gym_id claim."""
        gym = self._get_gym(db)
        email = random_email()
        password = random_lower_string()
        staff = self._create_staff(
            db, str(gym.id), email, password, StaffRole.FRONT_DESK
        )

        refresh_token = create_refresh_token(
            subject=str(staff.id),
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            role=staff.role.value,
            gym_id=str(staff.gym_id),
            token_version=staff.token_version,
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        result = response.json()

        # Verify gym_id is preserved
        assert result["gym_id"] == str(gym.id)

        # Also verify in the access token payload
        payload = jwt.decode(
            result["access_token"],
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )
        assert payload["gym_id"] == str(gym.id)

    def test_staff_refresh_expired_token(self, client: TestClient, db: Session) -> None:
        """Test expired staff refresh token returns 401 (AC #4)."""
        gym = self._get_gym(db)
        email = random_email()
        password = random_lower_string()
        staff = self._create_staff(db, str(gym.id), email, password)

        expired_token = create_refresh_token(
            subject=str(staff.id),
            expires_delta=timedelta(seconds=-10),
            role=staff.role.value,
            gym_id=str(staff.gym_id),
            token_version=staff.token_version,
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/refresh",
            json={"refresh_token": expired_token},
        )

        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_TOKEN"

    def test_staff_refresh_access_token_rejected(
        self, client: TestClient, db: Session
    ) -> None:
        """Test access token in staff refresh endpoint returns 401 (AC #4)."""
        gym = self._get_gym(db)
        email = random_email()
        password = random_lower_string()
        staff = self._create_staff(db, str(gym.id), email, password)

        # Use access token instead of refresh token
        access_token = create_access_token(
            subject=str(staff.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            role=staff.role.value,
            gym_id=str(staff.gym_id),
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/refresh",
            json={"refresh_token": access_token},
        )

        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_TOKEN"

    def test_staff_refresh_inactive_staff(
        self, client: TestClient, db: Session
    ) -> None:
        """Test inactive staff's refresh token returns 401 (AC #4)."""
        gym = self._get_gym(db)
        email = random_email()
        password = random_lower_string()
        staff = self._create_staff(db, str(gym.id), email, password, is_active=False)

        refresh_token = create_refresh_token(
            subject=str(staff.id),
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            role=staff.role.value,
            gym_id=str(staff.gym_id),
            token_version=staff.token_version,
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_TOKEN"

    def test_staff_refresh_all_roles(self, client: TestClient, db: Session) -> None:
        """Test token refresh works for all staff roles."""
        gym = self._get_gym(db)

        for role in StaffRole:
            email = random_email()
            password = random_lower_string()
            staff = self._create_staff(db, str(gym.id), email, password, role)

            refresh_token = create_refresh_token(
                subject=str(staff.id),
                expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                role=staff.role.value,
                gym_id=str(staff.gym_id),
                token_version=staff.token_version,
            )

            response = client.post(
                f"{settings.API_V1_STR}/auth/staff/refresh",
                json={"refresh_token": refresh_token},
            )

            assert response.status_code == 200
            result = response.json()
            assert result["role"] == role.value

    def test_staff_refresh_wrong_version_rejected(
        self, client: TestClient, db: Session
    ) -> None:
        """Test staff refresh token with wrong version returns 401 (AC #2)."""
        gym = self._get_gym(db)
        email = random_email()
        password = random_lower_string()
        staff = self._create_staff(db, str(gym.id), email, password)

        # Create token with wrong version
        wrong_version_token = create_refresh_token(
            subject=str(staff.id),
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            role=staff.role.value,
            gym_id=str(staff.gym_id),
            token_version=staff.token_version + 10,  # Wrong version
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/refresh",
            json={"refresh_token": wrong_version_token},
        )

        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_TOKEN"
