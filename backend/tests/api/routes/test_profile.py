"""Tests for user profile management endpoints (Story 1.6).

Tests cover:
- Consumer GET /me and PATCH /me endpoints
- Staff GET /me and PATCH /me endpoints
- SA phone number validation
- Authentication requirements
"""

from datetime import timedelta

from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
)
from app.models.consumer import Consumer, UserRole
from app.models.gym import Gym
from app.models.staff import Staff, StaffRole
from tests.utils.utils import random_email, random_lower_string


class TestConsumerGetMe:
    """Tests for GET /auth/consumer/me endpoint."""

    def test_get_me_success(self, client, db: Session):
        """Test GET /me returns consumer profile when authenticated."""
        # Create verified consumer
        email = random_email()
        password = "testpassword123"
        consumer = Consumer(
            email=email,
            first_name="Test",
            last_name="User",
            phone="+27821234567",
            hashed_password=get_password_hash(password),
            role=UserRole.CONSUMER,
            is_email_verified=True,
            is_active=True,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)

        # Generate access token
        access_token = create_access_token(
            subject=str(consumer.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        # Get profile
        response = client.get(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert data["phone"] == "+27821234567"
        assert data["role"] == "consumer"
        assert data["is_email_verified"] is True
        assert "hashed_password" not in data

    def test_get_me_no_token(self, client):
        """Test GET /me returns 401 when no token provided."""
        response = client.get(f"{settings.API_V1_STR}/auth/consumer/me")
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        """Test GET /me returns 401 when invalid token provided."""
        response = client.get(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    def test_get_me_refresh_token_rejected(self, client, db: Session):
        """Test GET /me returns 401 when refresh token used instead of access token."""
        # Create consumer
        email = random_email()
        consumer = Consumer(
            email=email,
            first_name="Test",
            last_name="User",
            hashed_password=get_password_hash("testpassword123"),
            role=UserRole.CONSUMER,
            is_email_verified=True,
            is_active=True,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)

        # Generate refresh token (not access token)
        refresh_token = create_refresh_token(
            subject=str(consumer.id),
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            token_version=consumer.token_version,
        )

        # Try to use refresh token as bearer
        response = client.get(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )

        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"

    def test_get_me_inactive_consumer(self, client, db: Session):
        """Test GET /me returns 401 when consumer is inactive."""
        # Create inactive consumer
        email = random_email()
        consumer = Consumer(
            email=email,
            first_name="Test",
            last_name="User",
            hashed_password=get_password_hash("testpassword123"),
            role=UserRole.CONSUMER,
            is_email_verified=True,
            is_active=False,  # Inactive
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)

        # Generate access token
        access_token = create_access_token(
            subject=str(consumer.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        response = client.get(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"


class TestConsumerPatchMe:
    """Tests for PATCH /auth/consumer/me endpoint."""

    def _create_consumer_with_token(self, db: Session) -> tuple[Consumer, str]:
        """Helper to create a verified consumer and return with access token."""
        email = random_email()
        consumer = Consumer(
            email=email,
            first_name="Test",
            last_name="User",
            hashed_password=get_password_hash("testpassword123"),
            role=UserRole.CONSUMER,
            is_email_verified=True,
            is_active=True,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)

        access_token = create_access_token(
            subject=str(consumer.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return consumer, access_token

    def test_patch_me_update_first_name(self, client, db: Session):
        """Test PATCH /me updates first_name only."""
        consumer, token = self._create_consumer_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "NewFirst"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "NewFirst"
        assert data["last_name"] == "User"  # Unchanged

    def test_patch_me_update_last_name(self, client, db: Session):
        """Test PATCH /me updates last_name only."""
        consumer, token = self._create_consumer_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"last_name": "NewLast"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Test"  # Unchanged
        assert data["last_name"] == "NewLast"

    def test_patch_me_update_phone_valid_sa_format(self, client, db: Session):
        """Test PATCH /me updates phone with valid SA format."""
        consumer, token = self._create_consumer_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"phone": "+27821234567"},
        )

        assert response.status_code == 200
        assert response.json()["phone"] == "+27821234567"

    def test_patch_me_phone_normalized(self, client, db: Session):
        """Test PATCH /me normalizes phone with spaces and dashes."""
        consumer, token = self._create_consumer_with_token(db)

        # Phone with spaces and dashes should be normalized
        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"phone": "+27 82 123-4567"},
        )

        assert response.status_code == 200
        assert response.json()["phone"] == "+27821234567"

    def test_patch_me_invalid_phone_missing_plus27(self, client, db: Session):
        """Test PATCH /me rejects phone without +27 prefix."""
        consumer, token = self._create_consumer_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"phone": "0821234567"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_PHONE_FORMAT"

    def test_patch_me_invalid_phone_wrong_country(self, client, db: Session):
        """Test PATCH /me rejects phone with wrong country code."""
        consumer, token = self._create_consumer_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"phone": "+1821234567"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_PHONE_FORMAT"

    def test_patch_me_invalid_phone_too_short(self, client, db: Session):
        """Test PATCH /me rejects phone that's too short."""
        consumer, token = self._create_consumer_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"phone": "+278212345"},  # Too short
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_PHONE_FORMAT"

    def test_patch_me_invalid_phone_too_long(self, client, db: Session):
        """Test PATCH /me rejects phone that's too long."""
        consumer, token = self._create_consumer_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"phone": "+2782123456789"},  # Too long
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_PHONE_FORMAT"

    def test_patch_me_clear_phone_with_null(self, client, db: Session):
        """Test PATCH /me clears phone when null is provided."""
        # Create consumer with phone
        email = random_email()
        consumer = Consumer(
            email=email,
            first_name="Test",
            last_name="User",
            phone="+27821234567",
            hashed_password=get_password_hash("testpassword123"),
            role=UserRole.CONSUMER,
            is_email_verified=True,
            is_active=True,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)

        access_token = create_access_token(
            subject=str(consumer.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"phone": None},
        )

        assert response.status_code == 200
        assert response.json()["phone"] is None

    def test_patch_me_multiple_fields(self, client, db: Session):
        """Test PATCH /me updates multiple fields at once."""
        consumer, token = self._create_consumer_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "first_name": "NewFirst",
                "last_name": "NewLast",
                "phone": "+27721234567",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "NewFirst"
        assert data["last_name"] == "NewLast"
        assert data["phone"] == "+27721234567"

    def test_patch_me_no_token(self, client):
        """Test PATCH /me returns 401 when not authenticated."""
        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            json={"first_name": "Test"},
        )
        assert response.status_code == 401

    def test_patch_me_rejects_null_first_name(self, client, db: Session):
        """Test PATCH /me rejects null for non-nullable first_name."""
        consumer, token = self._create_consumer_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": None},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_FIELD_VALUE"
        assert "first_name" in response.json()["detail"]["message"]

    def test_patch_me_rejects_null_last_name(self, client, db: Session):
        """Test PATCH /me rejects null for non-nullable last_name."""
        consumer, token = self._create_consumer_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"last_name": None},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_FIELD_VALUE"
        assert "last_name" in response.json()["detail"]["message"]

    def test_patch_me_rejects_null_accepts_marketing(self, client, db: Session):
        """Test PATCH /me rejects null for non-nullable accepts_marketing."""
        consumer, token = self._create_consumer_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"accepts_marketing": None},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_FIELD_VALUE"
        assert "accepts_marketing" in response.json()["detail"]["message"]


class TestStaffGetMe:
    """Tests for GET /auth/staff/me endpoint."""

    def _get_or_create_gym(self, db: Session) -> Gym:
        """Get existing gym or create one for tests."""
        gym = db.exec(select(Gym).where(Gym.is_active.is_(True))).first()
        if not gym:
            gym = Gym(
                name="Test Gym",
                slug=random_lower_string(),
                is_active=True,
            )
            db.add(gym)
            db.commit()
            db.refresh(gym)
        return gym

    def test_get_me_success(self, client, db: Session):
        """Test GET /me returns staff profile when authenticated."""
        gym = self._get_or_create_gym(db)

        # Create staff
        email = random_email()
        staff = Staff(
            email=email,
            first_name="Staff",
            last_name="Member",
            phone="+27821234567",
            hashed_password=get_password_hash("testpassword123"),
            role=StaffRole.MANAGER,
            gym_id=gym.id,
            is_active=True,
        )
        db.add(staff)
        db.commit()
        db.refresh(staff)

        # Generate access token
        access_token = create_access_token(
            subject=str(staff.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            role=staff.role.value,
            gym_id=str(staff.gym_id),
        )

        response = client.get(
            f"{settings.API_V1_STR}/auth/staff/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert data["first_name"] == "Staff"
        assert data["last_name"] == "Member"
        assert data["role"] == "manager"
        assert data["gym_id"] == str(gym.id)
        assert "hashed_password" not in data

    def test_get_me_no_token(self, client):
        """Test GET /me returns 401 when no token provided."""
        response = client.get(f"{settings.API_V1_STR}/auth/staff/me")
        assert response.status_code == 401

    def test_get_me_inactive_staff(self, client, db: Session):
        """Test GET /me returns 401 when staff is inactive."""
        gym = self._get_or_create_gym(db)

        # Create inactive staff
        email = random_email()
        staff = Staff(
            email=email,
            first_name="Staff",
            last_name="Member",
            hashed_password=get_password_hash("testpassword123"),
            role=StaffRole.FRONT_DESK,
            gym_id=gym.id,
            is_active=False,  # Inactive
        )
        db.add(staff)
        db.commit()
        db.refresh(staff)

        access_token = create_access_token(
            subject=str(staff.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            role=staff.role.value,
            gym_id=str(staff.gym_id),
        )

        response = client.get(
            f"{settings.API_V1_STR}/auth/staff/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"


class TestStaffPatchMe:
    """Tests for PATCH /auth/staff/me endpoint."""

    def _get_or_create_gym(self, db: Session) -> Gym:
        """Get existing gym or create one for tests."""
        gym = db.exec(select(Gym).where(Gym.is_active.is_(True))).first()
        if not gym:
            gym = Gym(
                name="Test Gym",
                slug=random_lower_string(),
                is_active=True,
            )
            db.add(gym)
            db.commit()
            db.refresh(gym)
        return gym

    def _create_staff_with_token(self, db: Session) -> tuple[Staff, str]:
        """Helper to create staff and return with access token."""
        gym = self._get_or_create_gym(db)
        email = random_email()
        staff = Staff(
            email=email,
            first_name="Staff",
            last_name="Member",
            hashed_password=get_password_hash("testpassword123"),
            role=StaffRole.INSTRUCTOR,
            gym_id=gym.id,
            is_active=True,
        )
        db.add(staff)
        db.commit()
        db.refresh(staff)

        access_token = create_access_token(
            subject=str(staff.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            role=staff.role.value,
            gym_id=str(staff.gym_id),
        )
        return staff, access_token

    def test_patch_me_update_profile_fields(self, client, db: Session):
        """Test PATCH /me updates staff profile fields."""
        staff, token = self._create_staff_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/staff/me",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "first_name": "NewFirst",
                "last_name": "NewLast",
                "phone": "+27821234567",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "NewFirst"
        assert data["last_name"] == "NewLast"
        assert data["phone"] == "+27821234567"

    def test_patch_me_invalid_phone(self, client, db: Session):
        """Test PATCH /me rejects invalid phone format."""
        staff, token = self._create_staff_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/staff/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"phone": "invalid"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_PHONE_FORMAT"

    def test_patch_me_role_preserved(self, client, db: Session):
        """Test PATCH /me preserves role (cannot be changed via profile)."""
        staff, token = self._create_staff_with_token(db)
        original_role = staff.role.value

        response = client.patch(
            f"{settings.API_V1_STR}/auth/staff/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Updated"},
        )

        assert response.status_code == 200
        assert response.json()["role"] == original_role

    def test_patch_me_gym_id_preserved(self, client, db: Session):
        """Test PATCH /me preserves gym_id (cannot be changed via profile)."""
        staff, token = self._create_staff_with_token(db)
        original_gym_id = str(staff.gym_id)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/staff/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Updated"},
        )

        assert response.status_code == 200
        assert response.json()["gym_id"] == original_gym_id

    def test_patch_me_rejects_null_first_name(self, client, db: Session):
        """Test PATCH /me rejects null for non-nullable first_name."""
        staff, token = self._create_staff_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/staff/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": None},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_FIELD_VALUE"
        assert "first_name" in response.json()["detail"]["message"]

    def test_patch_me_rejects_null_last_name(self, client, db: Session):
        """Test PATCH /me rejects null for non-nullable last_name."""
        staff, token = self._create_staff_with_token(db)

        response = client.patch(
            f"{settings.API_V1_STR}/auth/staff/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"last_name": None},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_FIELD_VALUE"
        assert "last_name" in response.json()["detail"]["message"]


class TestSAPhoneValidation:
    """Edge case tests for SA phone validation."""

    def _create_consumer_with_token(self, db: Session) -> tuple[Consumer, str]:
        """Helper to create a verified consumer and return with access token."""
        email = random_email()
        consumer = Consumer(
            email=email,
            first_name="Test",
            last_name="User",
            hashed_password=get_password_hash("testpassword123"),
            role=UserRole.CONSUMER,
            is_email_verified=True,
            is_active=True,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)

        access_token = create_access_token(
            subject=str(consumer.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return consumer, access_token

    def test_valid_mobile_82(self, client, db: Session):
        """Test +27 82 (mobile) is valid."""
        consumer, token = self._create_consumer_with_token(db)
        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"phone": "+27821234567"},
        )
        assert response.status_code == 200

    def test_valid_mobile_72(self, client, db: Session):
        """Test +27 72 (mobile) is valid."""
        consumer, token = self._create_consumer_with_token(db)
        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"phone": "+27721234567"},
        )
        assert response.status_code == 200

    def test_valid_landline_11(self, client, db: Session):
        """Test +27 11 (Johannesburg landline) is valid."""
        consumer, token = self._create_consumer_with_token(db)
        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"phone": "+27111234567"},
        )
        assert response.status_code == 200

    def test_invalid_missing_plus(self, client, db: Session):
        """Test phone missing + is invalid."""
        consumer, token = self._create_consumer_with_token(db)
        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"phone": "27821234567"},
        )
        assert response.status_code == 400
