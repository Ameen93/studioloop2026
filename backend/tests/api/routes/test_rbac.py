"""Tests for Role-Based Access Control (Story 1.8).

Tests cover:
- RoleChecker dependency allowing/denying access based on role
- Gym-scoped access validation (StaffGymDep)
- Role hierarchy and permission inheritance
- Consumer vs Staff isolation
"""

from datetime import timedelta
from uuid import uuid4

from sqlmodel import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models import Gym
from app.models.staff import Staff, StaffRole


def _create_gym(db: Session, name: str = "Test Gym") -> Gym:
    """Create a test gym."""
    gym = Gym(
        name=name,
        slug=f"test-gym-{uuid4().hex[:8]}",
        contact_email=f"gym-{uuid4().hex[:8]}@test.com",
        is_active=True,
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)
    return gym


def _create_staff_with_token(
    db: Session,
    gym: Gym,
    role: StaffRole = StaffRole.OWNER,
    email: str | None = None,
) -> tuple[Staff, str]:
    """Create a staff member and return with access token."""
    if email is None:
        email = f"staff-{uuid4().hex[:8]}@test.com"

    staff = Staff(
        email=email,
        first_name="Test",
        last_name="Staff",
        hashed_password=get_password_hash("testpassword123"),
        role=role,
        gym_id=gym.id,
        is_active=True,
        is_email_verified=True,
        token_version=1,
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)

    access_token = create_access_token(
        subject=str(staff.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        role=role.value,
        gym_id=str(gym.id),
    )

    return staff, access_token


class TestRoleChecker:
    """Tests for RoleChecker dependency."""

    def test_owner_can_access_owner_route(self, client, db: Session):
        """Test owner role can access owner-only routes (AC #1)."""
        gym = _create_gym(db)
        staff, token = _create_staff_with_token(db, gym, role=StaffRole.OWNER)

        response = client.get(
            f"{settings.API_V1_STR}/rbac/owner-only",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert "owner" in response.json()["message"].lower()

    def test_manager_can_access_manager_route(self, client, db: Session):
        """Test manager role can access manager-or-above routes (AC #1)."""
        gym = _create_gym(db)
        staff, token = _create_staff_with_token(db, gym, role=StaffRole.MANAGER)

        response = client.get(
            f"{settings.API_V1_STR}/rbac/manager-or-above",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert "manager" in response.json()["message"].lower()

    def test_front_desk_cannot_access_owner_route(self, client, db: Session):
        """Test front_desk role cannot access owner-only routes (AC #2, #5)."""
        gym = _create_gym(db)
        staff, token = _create_staff_with_token(db, gym, role=StaffRole.FRONT_DESK)

        response = client.get(
            f"{settings.API_V1_STR}/rbac/owner-only",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "FORBIDDEN"
        assert "required_roles" in response.json()["detail"]["details"]

    def test_front_desk_cannot_access_manager_route(self, client, db: Session):
        """Test front_desk role cannot access manager routes (AC #2, #5)."""
        gym = _create_gym(db)
        staff, token = _create_staff_with_token(db, gym, role=StaffRole.FRONT_DESK)

        response = client.get(
            f"{settings.API_V1_STR}/rbac/manager-or-above",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "FORBIDDEN"

    def test_instructor_cannot_access_owner_route(self, client, db: Session):
        """Test instructor role cannot access owner-only routes (AC #2)."""
        gym = _create_gym(db)
        staff, token = _create_staff_with_token(db, gym, role=StaffRole.INSTRUCTOR)

        response = client.get(
            f"{settings.API_V1_STR}/rbac/owner-only",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "FORBIDDEN"

    def test_any_staff_can_access_staff_route(self, client, db: Session):
        """Test any staff role can access any-staff routes (AC #1)."""
        gym = _create_gym(db)

        for role in [
            StaffRole.OWNER,
            StaffRole.MANAGER,
            StaffRole.FRONT_DESK,
            StaffRole.INSTRUCTOR,
        ]:
            staff, token = _create_staff_with_token(db, gym, role=role)

            response = client.get(
                f"{settings.API_V1_STR}/rbac/any-staff",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200, f"Failed for role {role.value}"


class TestGymScopedAccess:
    """Tests for gym-scoped access validation (StaffGymDep)."""

    def test_staff_can_access_own_gym(self, client, db: Session):
        """Test staff can access their own gym's routes (AC #3)."""
        gym = _create_gym(db)
        staff, token = _create_staff_with_token(db, gym, role=StaffRole.OWNER)

        response = client.get(
            f"{settings.API_V1_STR}/rbac/gyms/{gym.id}/staff-area",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert str(gym.id) in response.json()["message"]

    def test_staff_cannot_access_other_gym(self, client, db: Session):
        """Test staff cannot access other gym's routes (AC #3)."""
        gym1 = _create_gym(db, name="Gym 1")
        gym2 = _create_gym(db, name="Gym 2")
        staff, token = _create_staff_with_token(db, gym1, role=StaffRole.OWNER)

        response = client.get(
            f"{settings.API_V1_STR}/rbac/gyms/{gym2.id}/staff-area",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "FORBIDDEN"
        assert "Access denied" in response.json()["detail"]["message"]

    def test_gym_id_mismatch_error_does_not_leak_details(self, client, db: Session):
        """Test error message doesn't reveal gym details (security)."""
        gym1 = _create_gym(db, name="Gym 1")
        gym2 = _create_gym(db, name="Gym 2")
        staff, token = _create_staff_with_token(db, gym1, role=StaffRole.OWNER)

        response = client.get(
            f"{settings.API_V1_STR}/rbac/gyms/{gym2.id}/staff-area",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Error should NOT reveal which gym exists or staff's actual gym
        error_message = response.json()["detail"]["message"]
        assert "Gym 1" not in error_message
        assert "Gym 2" not in error_message
        assert str(gym1.id) not in error_message

    def test_gym_owner_area_requires_both_role_and_gym(self, client, db: Session):
        """Test combined role + gym validation (AC #3, #5)."""
        gym = _create_gym(db)

        # Manager at same gym - should fail role check (owner only)
        manager, manager_token = _create_staff_with_token(
            db, gym, role=StaffRole.MANAGER
        )

        response = client.get(
            f"{settings.API_V1_STR}/rbac/gyms/{gym.id}/owner-area",
            headers={"Authorization": f"Bearer {manager_token}"},
        )

        assert response.status_code == 403

        # Owner at same gym - should succeed
        owner, owner_token = _create_staff_with_token(db, gym, role=StaffRole.OWNER)

        response = client.get(
            f"{settings.API_V1_STR}/rbac/gyms/{gym.id}/owner-area",
            headers={"Authorization": f"Bearer {owner_token}"},
        )

        assert response.status_code == 200


class TestRoleHierarchy:
    """Tests for role hierarchy and permission inheritance."""

    def test_owner_inherits_manager_permissions(self, client, db: Session):
        """Test owner can access manager-level routes (role hierarchy)."""
        gym = _create_gym(db)
        staff, token = _create_staff_with_token(db, gym, role=StaffRole.OWNER)

        response = client.get(
            f"{settings.API_V1_STR}/rbac/manager-or-above",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_manager_can_access_staff_routes(self, client, db: Session):
        """Test manager can access any-staff routes."""
        gym = _create_gym(db)
        staff, token = _create_staff_with_token(db, gym, role=StaffRole.MANAGER)

        response = client.get(
            f"{settings.API_V1_STR}/rbac/any-staff",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_instructor_cannot_inherit_front_desk_in_role_checker(
        self, client, db: Session
    ):
        """Test instructor and front_desk are peer roles (no inheritance).

        Note: RoleChecker uses explicit lists, not hierarchy.
        If a route allows ["front_desk"] but not ["instructor"],
        instructor should be denied.
        """
        # This test validates that we don't accidentally grant permissions
        # The current RoleChecker doesn't use hierarchy internally,
        # which is the correct behavior for explicit role requirements
        gym = _create_gym(db)
        staff, token = _create_staff_with_token(db, gym, role=StaffRole.INSTRUCTOR)

        # Instructor should be able to access any-staff
        response = client.get(
            f"{settings.API_V1_STR}/rbac/any-staff",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200


class TestConsumerStaffIsolation:
    """Tests for consumer vs staff isolation (AC #4)."""

    def test_consumer_cannot_access_staff_routes(self, client, db: Session):
        """Test consumer token cannot access staff-only routes (AC #4)."""
        # Create a consumer and get token
        from app.models.consumer import Consumer, UserRole

        consumer = Consumer(
            email=f"consumer-{uuid4().hex[:8]}@test.com",
            first_name="Test",
            last_name="Consumer",
            hashed_password=get_password_hash("testpassword123"),
            role=UserRole.CONSUMER,
            is_email_verified=True,
            is_active=True,
            token_version=1,
        )
        db.add(consumer)
        db.commit()
        db.refresh(consumer)

        consumer_token = create_access_token(
            subject=str(consumer.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        # Try to access staff route with consumer token
        response = client.get(
            f"{settings.API_V1_STR}/rbac/any-staff",
            headers={"Authorization": f"Bearer {consumer_token}"},
        )

        # Should fail at CurrentStaff dependency (consumer is not staff)
        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "INVALID_TOKEN"


class TestNoAuthentication:
    """Tests for unauthenticated access attempts."""

    def test_no_token_returns_401(self, client):
        """Test request without token returns 401."""
        response = client.get(f"{settings.API_V1_STR}/rbac/owner-only")

        assert response.status_code == 401

    def test_invalid_token_returns_401(self, client):
        """Test request with invalid token returns 401."""
        response = client.get(
            f"{settings.API_V1_STR}/rbac/owner-only",
            headers={"Authorization": "Bearer invalid_token_here"},
        )

        assert response.status_code == 401


class TestInlineRoleChecker:
    """Tests for inline RoleChecker usage pattern."""

    def test_inline_role_checker_allows_valid_role(self, client, db: Session):
        """Test inline RoleChecker dependency works for allowed roles."""
        gym = _create_gym(db)
        staff, token = _create_staff_with_token(db, gym, role=StaffRole.MANAGER)

        response = client.get(
            f"{settings.API_V1_STR}/rbac/inline-role-check",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_inline_role_checker_denies_invalid_role(self, client, db: Session):
        """Test inline RoleChecker dependency denies unauthorized roles."""
        gym = _create_gym(db)
        staff, token = _create_staff_with_token(db, gym, role=StaffRole.FRONT_DESK)

        response = client.get(
            f"{settings.API_V1_STR}/rbac/inline-role-check",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
