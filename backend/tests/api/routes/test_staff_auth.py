"""Tests for staff authentication endpoints.

Verifies Story 1.3 acceptance criteria:
- AC #1: Staff receives JWT with role claims (owner/manager/front_desk/instructor)
- AC #2: Token includes gym_id for tenant context
- AC #4: Staff table created with gym_id FK (tested implicitly via model)
- AC #5: Inactive staff accounts cannot login
"""

import jwt
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Gym, Staff, StaffRole
from tests.utils.utils import random_email, random_lower_string


class TestStaffLogin:
    """Tests for POST /auth/staff/login endpoint."""

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
        )
        db.add(staff)
        db.commit()
        db.refresh(staff)
        return staff

    def _get_or_create_gym(self, db: Session) -> Gym:
        """Get existing gym or create one for testing."""
        gym = db.exec(select(Gym)).first()
        if gym:
            return gym

        gym = Gym(
            name="Test Gym",
            slug=f"test-gym-{random_lower_string()}",
            description="Test gym for staff auth tests",
        )
        db.add(gym)
        db.commit()
        db.refresh(gym)
        return gym

    def test_staff_login_success_owner(self, client: TestClient, db: Session) -> None:
        """Test successful staff login returns tokens with role/gym_id (AC #1, #2)."""
        gym = self._get_or_create_gym(db)
        email = random_email()
        password = random_lower_string()
        self._create_staff(db, str(gym.id), email, password, StaffRole.OWNER)

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/login",
            json={"email": email, "password": password},
        )

        assert response.status_code == 200
        result = response.json()

        # Verify token response structure
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert result["role"] == "owner"
        assert result["gym_id"] == str(gym.id)

        # Verify tokens are non-empty strings
        assert isinstance(result["access_token"], str)
        assert len(result["access_token"]) > 0
        assert isinstance(result["refresh_token"], str)
        assert len(result["refresh_token"]) > 0

    def test_staff_login_manager_role(self, client: TestClient, db: Session) -> None:
        """Test manager login returns role: manager (AC #1)."""
        gym = self._get_or_create_gym(db)
        email = random_email()
        password = random_lower_string()
        self._create_staff(db, str(gym.id), email, password, StaffRole.MANAGER)

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/login",
            json={"email": email, "password": password},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["role"] == "manager"

    def test_staff_login_front_desk_role(self, client: TestClient, db: Session) -> None:
        """Test front_desk login returns role: front_desk (AC #1)."""
        gym = self._get_or_create_gym(db)
        email = random_email()
        password = random_lower_string()
        self._create_staff(db, str(gym.id), email, password, StaffRole.FRONT_DESK)

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/login",
            json={"email": email, "password": password},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["role"] == "front_desk"

    def test_staff_login_instructor_role(self, client: TestClient, db: Session) -> None:
        """Test instructor login returns role: instructor (AC #1)."""
        gym = self._get_or_create_gym(db)
        email = random_email()
        password = random_lower_string()
        self._create_staff(db, str(gym.id), email, password, StaffRole.INSTRUCTOR)

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/login",
            json={"email": email, "password": password},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["role"] == "instructor"

    def test_staff_token_has_role_claim(self, client: TestClient, db: Session) -> None:
        """Test JWT payload contains role claim (AC #1)."""
        gym = self._get_or_create_gym(db)
        email = random_email()
        password = random_lower_string()
        staff = self._create_staff(db, str(gym.id), email, password, StaffRole.OWNER)

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/login",
            json={"email": email, "password": password},
        )

        assert response.status_code == 200
        result = response.json()

        # Decode and verify access token payload
        payload = jwt.decode(
            result["access_token"],
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )

        assert payload["sub"] == str(staff.id)
        assert payload["type"] == "access"
        assert payload["role"] == "owner"
        assert payload["gym_id"] == str(gym.id)

    def test_staff_token_has_gym_id_claim(
        self, client: TestClient, db: Session
    ) -> None:
        """Test JWT payload contains gym_id claim (AC #2)."""
        gym = self._get_or_create_gym(db)
        email = random_email()
        password = random_lower_string()
        self._create_staff(db, str(gym.id), email, password, StaffRole.MANAGER)

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/login",
            json={"email": email, "password": password},
        )

        assert response.status_code == 200
        result = response.json()

        # Decode and verify access token payload
        payload = jwt.decode(
            result["access_token"],
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )

        assert "gym_id" in payload
        assert payload["gym_id"] == str(gym.id)

    def test_staff_login_invalid_password(
        self, client: TestClient, db: Session
    ) -> None:
        """Test login with wrong password returns 401 INVALID_CREDENTIALS."""
        gym = self._get_or_create_gym(db)
        email = random_email()
        password = random_lower_string()
        self._create_staff(db, str(gym.id), email, password, StaffRole.OWNER)

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/login",
            json={"email": email, "password": "wrongpassword123"},
        )

        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_CREDENTIALS"
        assert result["detail"]["message"] == "Invalid email or password"

    def test_staff_login_nonexistent_email(self, client: TestClient) -> None:
        """Test login with non-existent email returns 401 (same as invalid password)."""
        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/login",
            json={"email": "nonexistent@example.com", "password": "anypassword123"},
        )

        # Should return same error to prevent email enumeration
        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_CREDENTIALS"

    def test_staff_login_inactive_account(
        self, client: TestClient, db: Session
    ) -> None:
        """Test login with inactive staff returns 401 INVALID_CREDENTIALS (AC #5)."""
        gym = self._get_or_create_gym(db)
        email = random_email()
        password = random_lower_string()
        self._create_staff(
            db, str(gym.id), email, password, StaffRole.OWNER, is_active=False
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/login",
            json={"email": email, "password": password},
        )

        # Should return same error as invalid credentials (no status enumeration)
        assert response.status_code == 401
        result = response.json()
        assert result["detail"]["code"] == "INVALID_CREDENTIALS"

    def test_staff_login_short_password_validation(self, client: TestClient) -> None:
        """Test login with password < 8 chars returns 422 validation error."""
        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/login",
            json={"email": "test@example.com", "password": "short"},
        )

        assert response.status_code == 422

    def test_staff_login_invalid_email_format(self, client: TestClient) -> None:
        """Test login with invalid email format returns 422 validation error."""
        response = client.post(
            f"{settings.API_V1_STR}/auth/staff/login",
            json={"email": "not-an-email", "password": "testpassword123"},
        )

        assert response.status_code == 422


class TestStaffModel:
    """Tests for Staff model structure (AC #4)."""

    def test_staff_belongs_to_gym(self, db: Session) -> None:
        """Test staff has gym_id FK relationship."""
        gym = db.exec(select(Gym)).first()
        if not gym:
            gym = Gym(
                name="Test Gym for Model",
                slug=f"test-gym-model-{random_lower_string()}",
            )
            db.add(gym)
            db.commit()
            db.refresh(gym)

        staff = Staff(
            gym_id=gym.id,
            email=random_email(),
            hashed_password=get_password_hash("testpassword123"),
            first_name="Model",
            last_name="Test",
            role=StaffRole.OWNER,
        )
        db.add(staff)
        db.commit()
        db.refresh(staff)

        # Verify gym relationship
        assert staff.gym_id == gym.id
        assert staff.gym.id == gym.id
        assert staff.gym.name == gym.name

    def test_staff_role_enum(self, db: Session) -> None:
        """Test all staff roles can be created."""
        gym = db.exec(select(Gym)).first()
        if not gym:
            gym = Gym(
                name="Test Gym for Roles",
                slug=f"test-gym-roles-{random_lower_string()}",
            )
            db.add(gym)
            db.commit()
            db.refresh(gym)

        for role in StaffRole:
            staff = Staff(
                gym_id=gym.id,
                email=random_email(),
                hashed_password=get_password_hash("testpassword123"),
                first_name=f"Test{role.value}",
                last_name="Staff",
                role=role,
            )
            db.add(staff)
            db.commit()
            db.refresh(staff)

            assert staff.role == role
            assert staff.role.value in ["owner", "manager", "front_desk", "instructor"]
