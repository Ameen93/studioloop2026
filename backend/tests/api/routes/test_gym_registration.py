"""Tests for gym registration endpoint.

Verifies Story 2.1 acceptance criteria:
- AC #1: Registration creates Consumer with role: owner and unique email
- AC #2: Gym record created with provided details
- AC #3: Staff record links owner to gym with role: owner
- AC #4: Verification email sent after registration
- AC #5: Unique URL-friendly slug generated from gym name
- AC #6: Duplicate emails rejected with EMAIL_ALREADY_EXISTS
"""

from unittest.mock import patch
from uuid import UUID

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import verify_password
from app.models import Consumer, Gym, Staff, StaffRole, UserRole
from tests.utils.utils import random_email, random_lower_string


class TestGymRegistration:
    """Tests for POST /auth/gym/register endpoint."""

    def test_register_gym_success_creates_all_records(
        self, client: TestClient, db: Session
    ) -> None:
        """Test successful registration creates Consumer, Gym, and Staff records (AC #1, #2, #3)."""
        email = random_email()
        password = random_lower_string()
        data = {
            "email": email,
            "password": password,
            "first_name": "John",
            "last_name": "Owner",
            "gym_name": "Awesome Fitness Studio",
            "gym_contact_email": "contact@awesomefitness.com",
            "gym_contact_phone": "+27821234567",
        }

        with patch("app.api.routes.gyms.send_email"):
            response = client.post(
                f"{settings.API_V1_STR}/auth/gym/register",
                json=data,
            )

        assert response.status_code == 201
        result = response.json()

        # Verify response contains all required IDs (AC #8 equivalent)
        assert UUID(result["owner_id"])
        assert UUID(result["gym_id"])
        assert UUID(result["staff_id"])
        assert result["email"] == email
        assert result["gym_name"] == "Awesome Fitness Studio"
        assert "gym_slug" in result
        assert result["message"] == "Registration successful. Please verify your email."

        # Verify Consumer exists with role: owner (AC #1)
        consumer = db.exec(select(Consumer).where(Consumer.email == email)).first()
        assert consumer is not None
        assert consumer.role == UserRole.OWNER
        assert consumer.first_name == "John"
        assert consumer.last_name == "Owner"
        assert consumer.is_email_verified is False
        assert verify_password(password, consumer.hashed_password)

        # Verify Gym exists with correct details (AC #2)
        gym = db.exec(select(Gym).where(Gym.id == UUID(result["gym_id"]))).first()
        assert gym is not None
        assert gym.name == "Awesome Fitness Studio"
        assert gym.contact_email == "contact@awesomefitness.com"
        assert gym.contact_phone == "+27821234567"

        # Verify Staff exists with role: owner and correct gym_id (AC #3)
        staff = db.exec(select(Staff).where(Staff.email == email)).first()
        assert staff is not None
        assert staff.role == StaffRole.OWNER
        assert staff.gym_id == gym.id
        assert staff.first_name == "John"
        assert staff.last_name == "Owner"
        assert verify_password(password, staff.hashed_password)

    def test_register_gym_consumer_has_owner_role(
        self, client: TestClient, db: Session
    ) -> None:
        """Test Consumer created with role: owner (AC #1)."""
        email = random_email()
        data = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "Jane",
            "last_name": "Doe",
            "gym_name": "Test Gym",
        }

        with patch("app.api.routes.gyms.send_email"):
            response = client.post(
                f"{settings.API_V1_STR}/auth/gym/register",
                json=data,
            )

        assert response.status_code == 201

        consumer = db.exec(select(Consumer).where(Consumer.email == email)).first()
        assert consumer.role == UserRole.OWNER

    def test_register_gym_staff_has_owner_role_and_correct_gym_id(
        self, client: TestClient, db: Session
    ) -> None:
        """Test Staff has role: owner and correct gym_id (AC #3)."""
        email = random_email()
        data = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "Owner",
            "gym_name": "My Fitness Center",
        }

        with patch("app.api.routes.gyms.send_email"):
            response = client.post(
                f"{settings.API_V1_STR}/auth/gym/register",
                json=data,
            )

        assert response.status_code == 201
        result = response.json()

        staff = db.exec(select(Staff).where(Staff.email == email)).first()
        assert staff.role == StaffRole.OWNER
        assert str(staff.gym_id) == result["gym_id"]

    def test_register_gym_sends_verification_email(self, client: TestClient) -> None:
        """Test verification email is sent after registration (AC #4)."""
        email = random_email()
        data = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "User",
            "gym_name": "Email Test Gym",
        }

        with (
            patch("app.api.routes.gyms.send_email") as mock_send,
            patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
            patch("app.core.config.settings.EMAILS_FROM_EMAIL", "noreply@example.com"),
        ):
            response = client.post(
                f"{settings.API_V1_STR}/auth/gym/register",
                json=data,
            )

        assert response.status_code == 201
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert call_args.kwargs["email_to"] == email

    def test_register_gym_duplicate_email_in_consumer_table(
        self, client: TestClient, db: Session
    ) -> None:
        """Test duplicate email in Consumer table returns EMAIL_ALREADY_EXISTS (AC #6)."""
        email = random_email()

        # First registration
        data1 = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "First",
            "last_name": "Owner",
            "gym_name": "First Gym",
        }
        with patch("app.api.routes.gyms.send_email"):
            response1 = client.post(
                f"{settings.API_V1_STR}/auth/gym/register",
                json=data1,
            )
        assert response1.status_code == 201

        # Second registration with same email
        data2 = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "Second",
            "last_name": "Owner",
            "gym_name": "Second Gym",
        }
        response2 = client.post(
            f"{settings.API_V1_STR}/auth/gym/register",
            json=data2,
        )

        assert response2.status_code == 400
        result = response2.json()
        assert result["detail"]["code"] == "EMAIL_ALREADY_EXISTS"
        assert result["detail"]["message"] == "An account with this email already exists"
        assert result["detail"]["details"]["field"] == "email"

    def test_register_gym_duplicate_email_in_staff_table(
        self, client: TestClient, db: Session
    ) -> None:
        """Test duplicate email in Staff table returns EMAIL_ALREADY_EXISTS."""
        # Create a Staff record directly (simulating a staff member added by another gym)
        from app.core.security import get_password_hash

        existing_email = random_email()

        # First create a gym to link the staff to
        gym = Gym(
            name="Existing Gym",
            slug="existing-gym-test",
            contact_email="existing@gym.com",
        )
        db.add(gym)
        db.flush()

        staff = Staff(
            email=existing_email,
            first_name="Existing",
            last_name="Staff",
            hashed_password=get_password_hash("password123"),
            role=StaffRole.MANAGER,
            gym_id=gym.id,
        )
        db.add(staff)
        db.commit()

        # Try to register gym with same email
        data = {
            "email": existing_email,
            "password": random_lower_string(),
            "first_name": "New",
            "last_name": "Owner",
            "gym_name": "New Gym",
        }
        response = client.post(
            f"{settings.API_V1_STR}/auth/gym/register",
            json=data,
        )

        assert response.status_code == 400
        result = response.json()
        assert result["detail"]["code"] == "EMAIL_ALREADY_EXISTS"

    def test_register_gym_slug_generation_from_name(
        self, client: TestClient, db: Session
    ) -> None:
        """Test unique URL-friendly slug generated from gym name (AC #5)."""
        email = random_email()
        data = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "Owner",
            "gym_name": "My Awesome Gym!!! @2024",
        }

        with patch("app.api.routes.gyms.send_email"):
            response = client.post(
                f"{settings.API_V1_STR}/auth/gym/register",
                json=data,
            )

        assert response.status_code == 201
        result = response.json()

        # Slug should be lowercase, hyphenated, no special chars
        assert result["gym_slug"] == "my-awesome-gym-2024"

        # Verify in database
        gym = db.exec(select(Gym).where(Gym.slug == "my-awesome-gym-2024")).first()
        assert gym is not None
        assert gym.name == "My Awesome Gym!!! @2024"

    def test_register_gym_slug_collision_handling(
        self, client: TestClient, db: Session
    ) -> None:
        """Test slug collision appends numeric suffix."""
        # First gym
        data1 = {
            "email": random_email(),
            "password": random_lower_string(),
            "first_name": "First",
            "last_name": "Owner",
            "gym_name": "Cool Gym",
        }
        with patch("app.api.routes.gyms.send_email"):
            response1 = client.post(
                f"{settings.API_V1_STR}/auth/gym/register",
                json=data1,
            )
        assert response1.status_code == 201
        assert response1.json()["gym_slug"] == "cool-gym"

        # Second gym with same name
        data2 = {
            "email": random_email(),
            "password": random_lower_string(),
            "first_name": "Second",
            "last_name": "Owner",
            "gym_name": "Cool Gym",
        }
        with patch("app.api.routes.gyms.send_email"):
            response2 = client.post(
                f"{settings.API_V1_STR}/auth/gym/register",
                json=data2,
            )
        assert response2.status_code == 201
        assert response2.json()["gym_slug"] == "cool-gym-1"

        # Third gym with same name
        data3 = {
            "email": random_email(),
            "password": random_lower_string(),
            "first_name": "Third",
            "last_name": "Owner",
            "gym_name": "Cool Gym",
        }
        with patch("app.api.routes.gyms.send_email"):
            response3 = client.post(
                f"{settings.API_V1_STR}/auth/gym/register",
                json=data3,
            )
        assert response3.status_code == 201
        assert response3.json()["gym_slug"] == "cool-gym-2"

    def test_register_gym_password_validation_min_length(
        self, client: TestClient
    ) -> None:
        """Test password must be at least 8 characters."""
        data = {
            "email": random_email(),
            "password": "short",  # Only 5 characters
            "first_name": "Test",
            "last_name": "Owner",
            "gym_name": "Test Gym",
        }

        response = client.post(
            f"{settings.API_V1_STR}/auth/gym/register",
            json=data,
        )

        assert response.status_code == 422

    def test_register_gym_response_contains_all_ids(
        self, client: TestClient, db: Session
    ) -> None:
        """Test response contains owner_id, gym_id, staff_id as valid UUIDs."""
        email = random_email()
        data = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "Owner",
            "gym_name": "ID Test Gym",
        }

        with patch("app.api.routes.gyms.send_email"):
            response = client.post(
                f"{settings.API_V1_STR}/auth/gym/register",
                json=data,
            )

        assert response.status_code == 201
        result = response.json()

        # All IDs should be valid UUIDs
        owner_id = UUID(result["owner_id"])
        gym_id = UUID(result["gym_id"])
        staff_id = UUID(result["staff_id"])

        # Verify IDs match database records
        consumer = db.exec(select(Consumer).where(Consumer.id == owner_id)).first()
        assert consumer is not None
        assert consumer.email == email

        gym = db.exec(select(Gym).where(Gym.id == gym_id)).first()
        assert gym is not None
        assert gym.name == "ID Test Gym"

        staff = db.exec(select(Staff).where(Staff.id == staff_id)).first()
        assert staff is not None
        assert staff.gym_id == gym_id

    def test_register_gym_defaults_contact_email_to_owner_email(
        self, client: TestClient, db: Session
    ) -> None:
        """Test gym_contact_email defaults to owner email if not provided."""
        email = random_email()
        data = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "Owner",
            "gym_name": "Default Contact Gym",
            # gym_contact_email not provided
        }

        with patch("app.api.routes.gyms.send_email"):
            response = client.post(
                f"{settings.API_V1_STR}/auth/gym/register",
                json=data,
            )

        assert response.status_code == 201
        result = response.json()

        gym = db.exec(select(Gym).where(Gym.id == UUID(result["gym_id"]))).first()
        assert gym.contact_email == email  # Should default to owner email

    def test_register_gym_missing_required_fields(self, client: TestClient) -> None:
        """Test missing required fields return 422."""
        # Missing gym_name
        data = {
            "email": random_email(),
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "Owner",
        }

        response = client.post(
            f"{settings.API_V1_STR}/auth/gym/register",
            json=data,
        )

        assert response.status_code == 422

    def test_register_gym_empty_gym_name(self, client: TestClient) -> None:
        """Test empty gym_name returns 422."""
        data = {
            "email": random_email(),
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "Owner",
            "gym_name": "",  # Empty
        }

        response = client.post(
            f"{settings.API_V1_STR}/auth/gym/register",
            json=data,
        )

        assert response.status_code == 422

    def test_register_gym_special_chars_only_gym_name(
        self, client: TestClient, db: Session
    ) -> None:
        """Test gym name with only special chars gets default 'gym' slug."""
        email = random_email()
        data = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "Owner",
            "gym_name": "!@#$%",  # Only special chars
        }

        with patch("app.api.routes.gyms.send_email"):
            response = client.post(
                f"{settings.API_V1_STR}/auth/gym/register",
                json=data,
            )

        assert response.status_code == 201
        result = response.json()
        assert result["gym_slug"] == "gym"  # Default fallback

    def test_register_gym_staff_is_email_verified_false(
        self, client: TestClient, db: Session
    ) -> None:
        """Test Staff record is created with is_email_verified=False."""
        email = random_email()
        data = {
            "email": email,
            "password": random_lower_string(),
            "first_name": "Test",
            "last_name": "Owner",
            "gym_name": "Verification Test Gym",
        }

        with patch("app.api.routes.gyms.send_email"):
            response = client.post(
                f"{settings.API_V1_STR}/auth/gym/register",
                json=data,
            )

        assert response.status_code == 201

        staff = db.exec(select(Staff).where(Staff.email == email)).first()
        assert staff.is_email_verified is False
