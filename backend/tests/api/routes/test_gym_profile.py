"""Tests for gym profile configuration endpoints.

Verifies Story 2.2 acceptance criteria:
- AC #1: Update gym name, description, and tagline
- AC #2: Upload logo and cover photos
- AC #3: Set gym address with map location (lat/lng)
- AC #4: Add contact email and phone number
- AC #5: Changes visible on public profile
- AC #6: Photo file type and size validation
"""

import io
import json
from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models import Gym, Staff, StaffRole
from tests.utils.utils import random_email, random_lower_string


def create_test_gym(db: Session) -> Gym:
    """Create a test gym for tests."""
    gym = Gym(
        name="Test Gym",
        slug=f"test-gym-{uuid4().hex[:8]}",
        contact_email="test@gym.com",
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)
    return gym


def create_test_staff(db: Session, gym: Gym, role: StaffRole = StaffRole.OWNER) -> tuple[Staff, str]:
    """Create a test staff member and return (staff, access_token)."""
    staff = Staff(
        email=random_email(),
        first_name="Test",
        last_name="Staff",
        hashed_password=get_password_hash("password123"),
        role=role,
        gym_id=gym.id,
        is_email_verified=True,
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)

    # Create access token
    token = create_access_token(
        subject=str(staff.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return staff, token


class TestGymPublicProfile:
    """Tests for GET /gyms/{gym_id} and GET /gyms/by-slug/{slug} endpoints."""

    def test_get_gym_by_id(self, client: TestClient, db: Session) -> None:
        """Test getting gym by ID (no auth required)."""
        gym = create_test_gym(db)

        response = client.get(f"{settings.API_V1_STR}/gyms/{gym.id}")

        assert response.status_code == 200
        result = response.json()
        assert result["id"] == str(gym.id)
        assert result["name"] == "Test Gym"
        assert result["slug"] == gym.slug

    def test_get_gym_by_slug(self, client: TestClient, db: Session) -> None:
        """Test getting gym by slug (no auth required)."""
        gym = create_test_gym(db)

        response = client.get(f"{settings.API_V1_STR}/gyms/by-slug/{gym.slug}")

        assert response.status_code == 200
        result = response.json()
        assert result["slug"] == gym.slug
        assert result["name"] == "Test Gym"

    def test_get_gym_not_found(self, client: TestClient) -> None:
        """Test getting non-existent gym returns 404."""
        response = client.get(f"{settings.API_V1_STR}/gyms/{uuid4()}")

        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "GYM_NOT_FOUND"

    def test_get_gym_by_slug_not_found(self, client: TestClient) -> None:
        """Test getting non-existent gym by slug returns 404."""
        response = client.get(f"{settings.API_V1_STR}/gyms/by-slug/non-existent-slug")

        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "GYM_NOT_FOUND"


class TestGymProfileUpdate:
    """Tests for PUT /gyms/{gym_id}/profile endpoint."""

    def test_update_profile_success(self, client: TestClient, db: Session) -> None:
        """Test successful profile update (AC #1, #4, #5)."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        update_data = {
            "name": "Updated Gym Name",
            "description": "A great gym for fitness enthusiasts",
            "tagline": "Get fit, stay healthy!",
            "contact_email": "updated@gym.com",
            "contact_phone": "+27821234567",
        }

        response = client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "Updated Gym Name"
        assert result["description"] == "A great gym for fitness enthusiasts"
        assert result["tagline"] == "Get fit, stay healthy!"
        assert result["contact_email"] == "updated@gym.com"
        assert result["contact_phone"] == "+27821234567"

    def test_update_profile_partial(self, client: TestClient, db: Session) -> None:
        """Test partial profile update (only some fields)."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        # Only update tagline
        response = client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/profile",
            json={"tagline": "New tagline"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["tagline"] == "New tagline"
        assert result["name"] == "Test Gym"  # Unchanged

    def test_update_profile_requires_auth(self, client: TestClient, db: Session) -> None:
        """Test profile update requires authentication."""
        gym = create_test_gym(db)

        response = client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/profile",
            json={"name": "New Name"},
        )

        assert response.status_code == 401

    def test_update_profile_requires_owner_or_manager(
        self, client: TestClient, db: Session
    ) -> None:
        """Test profile update requires owner or manager role."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.INSTRUCTOR)

        response = client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/profile",
            json={"name": "New Name"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "FORBIDDEN"

    def test_update_profile_manager_allowed(self, client: TestClient, db: Session) -> None:
        """Test manager can update profile."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.MANAGER)

        response = client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/profile",
            json={"tagline": "Manager updated this"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["tagline"] == "Manager updated this"

    def test_update_profile_wrong_gym_forbidden(
        self, client: TestClient, db: Session
    ) -> None:
        """Test staff cannot update profile of another gym."""
        gym1 = create_test_gym(db)
        gym2 = create_test_gym(db)
        staff, token = create_test_staff(db, gym1, StaffRole.OWNER)

        response = client.put(
            f"{settings.API_V1_STR}/gyms/{gym2.id}/profile",
            json={"name": "Hacked Name"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403


class TestGymAddressUpdate:
    """Tests for PUT /gyms/{gym_id}/address endpoint."""

    def test_update_address_success(self, client: TestClient, db: Session) -> None:
        """Test successful address update (AC #3)."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        address_data = {
            "address_line1": "123 Main Street",
            "address_line2": "Suite 100",
            "city": "Johannesburg",
            "province": "Gauteng",
            "postal_code": "2196",
            "country": "ZA",
            "latitude": -26.1076,
            "longitude": 28.0567,
        }

        response = client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/address",
            json=address_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["address_line1"] == "123 Main Street"
        assert result["city"] == "Johannesburg"
        assert result["latitude"] == -26.1076
        assert result["longitude"] == 28.0567

    def test_update_address_invalid_latitude(
        self, client: TestClient, db: Session
    ) -> None:
        """Test address update rejects invalid latitude (outside SA bounds)."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        response = client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/address",
            json={"latitude": 0, "longitude": 28},  # Equator, not in SA
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_COORDINATES"

    def test_update_address_invalid_longitude(
        self, client: TestClient, db: Session
    ) -> None:
        """Test address update rejects invalid longitude (outside SA bounds)."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        response = client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/address",
            json={"latitude": -26, "longitude": 0},  # Atlantic Ocean
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_COORDINATES"

    def test_update_address_without_coordinates(
        self, client: TestClient, db: Session
    ) -> None:
        """Test address update without coordinates is allowed."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        response = client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/address",
            json={"city": "Cape Town"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["city"] == "Cape Town"


class TestGymPhotoUpload:
    """Tests for photo upload endpoints (AC #2, #6)."""

    def test_upload_logo_success(self, client: TestClient, db: Session) -> None:
        """Test successful logo upload."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        # Create a fake image file
        file_content = b"fake image content"
        files = {"file": ("logo.jpg", io.BytesIO(file_content), "image/jpeg")}

        response = client.post(
            f"{settings.API_V1_STR}/gyms/{gym.id}/logo",
            files=files,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        result = response.json()
        assert "url" in result
        assert f"/uploads/gyms/{gym.id}/logo" in result["url"]

        # Verify gym record updated
        db.refresh(gym)
        assert gym.logo_url is not None

    def test_upload_logo_invalid_file_type(
        self, client: TestClient, db: Session
    ) -> None:
        """Test logo upload rejects invalid file type."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        files = {"file": ("logo.pdf", io.BytesIO(b"fake pdf"), "application/pdf")}

        response = client.post(
            f"{settings.API_V1_STR}/gyms/{gym.id}/logo",
            files=files,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_FILE_TYPE"

    def test_upload_logo_file_too_large(
        self, client: TestClient, db: Session
    ) -> None:
        """Test logo upload rejects file over 5MB."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        # Create a file larger than 5MB
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        files = {"file": ("logo.jpg", io.BytesIO(large_content), "image/jpeg")}

        response = client.post(
            f"{settings.API_V1_STR}/gyms/{gym.id}/logo",
            files=files,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "FILE_TOO_LARGE"

    def test_upload_gallery_photo_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test successful gallery photo upload."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        files = {"file": ("photo.png", io.BytesIO(b"fake image"), "image/png")}

        response = client.post(
            f"{settings.API_V1_STR}/gyms/{gym.id}/photos",
            files=files,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        result = response.json()
        assert "url" in result
        assert f"/uploads/gyms/{gym.id}/photos/" in result["url"]

        # Verify gym record updated
        db.refresh(gym)
        assert len(gym.photo_urls) == 1

    def test_upload_multiple_photos(self, client: TestClient, db: Session) -> None:
        """Test uploading multiple gallery photos."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        # Upload first photo
        files1 = {"file": ("photo1.jpg", io.BytesIO(b"image1"), "image/jpeg")}
        client.post(
            f"{settings.API_V1_STR}/gyms/{gym.id}/photos",
            files=files1,
            headers={"Authorization": f"Bearer {token}"},
        )

        # Upload second photo
        files2 = {"file": ("photo2.jpg", io.BytesIO(b"image2"), "image/jpeg")}
        client.post(
            f"{settings.API_V1_STR}/gyms/{gym.id}/photos",
            files=files2,
            headers={"Authorization": f"Bearer {token}"},
        )

        # Verify both photos in gallery
        db.refresh(gym)
        assert len(gym.photo_urls) == 2

    def test_delete_gallery_photo(self, client: TestClient, db: Session) -> None:
        """Test deleting a gallery photo."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        # Upload a photo first
        files = {"file": ("photo.jpg", io.BytesIO(b"image"), "image/jpeg")}
        upload_response = client.post(
            f"{settings.API_V1_STR}/gyms/{gym.id}/photos",
            files=files,
            headers={"Authorization": f"Bearer {token}"},
        )
        photo_url = upload_response.json()["url"]

        # Delete the photo
        response = client.request(
            "DELETE",
            f"{settings.API_V1_STR}/gyms/{gym.id}/photos",
            content=json.dumps({"photo_url": photo_url}),
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )

        assert response.status_code == 200
        db.refresh(gym)
        assert photo_url not in gym.photo_urls

    def test_delete_nonexistent_photo(self, client: TestClient, db: Session) -> None:
        """Test deleting non-existent photo returns error."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        response = client.request(
            "DELETE",
            f"{settings.API_V1_STR}/gyms/{gym.id}/photos",
            content=json.dumps({"photo_url": "/uploads/gyms/fake/photo.jpg"}),
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "PHOTO_NOT_FOUND"


class TestGymProfileVisibility:
    """Tests for profile changes being visible (AC #5)."""

    def test_profile_changes_visible_on_public_endpoint(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that profile changes are visible on public profile."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        # Update profile
        client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/profile",
            json={"tagline": "Visible tagline"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Fetch public profile (no auth)
        response = client.get(f"{settings.API_V1_STR}/gyms/{gym.id}")

        assert response.status_code == 200
        assert response.json()["tagline"] == "Visible tagline"

    def test_address_changes_visible_on_public_endpoint(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that address changes are visible on public profile."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        # Update address
        client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/address",
            json={"city": "Durban", "province": "KwaZulu-Natal"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Fetch public profile
        response = client.get(f"{settings.API_V1_STR}/gyms/by-slug/{gym.slug}")

        assert response.status_code == 200
        assert response.json()["city"] == "Durban"
        assert response.json()["province"] == "KwaZulu-Natal"


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_invalid_uuid_format_returns_422(self, client: TestClient) -> None:
        """Test that invalid UUID format returns 422, not 500."""
        response = client.get(f"{settings.API_V1_STR}/gyms/not-a-uuid")

        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "INVALID_UUID"

    def test_invalid_uuid_on_profile_update(
        self, client: TestClient, db: Session
    ) -> None:
        """Test invalid UUID on profile update returns 422."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        response = client.put(
            f"{settings.API_V1_STR}/gyms/invalid-uuid/profile",
            json={"name": "Test"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # The endpoint returns 422 for invalid UUID
        # StaffGymDep validates gym_id before our validation runs
        assert response.status_code == 422

    def test_null_values_ignored_on_profile_update(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that explicit null values don't overwrite non-nullable fields."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        # Try to set name to null (name is non-nullable)
        response = client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/profile",
            json={"name": None, "tagline": "New tagline"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        result = response.json()
        # name should be unchanged (not null)
        assert result["name"] == "Test Gym"
        # tagline should be updated
        assert result["tagline"] == "New tagline"

    def test_single_latitude_update_validates_bounds(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that updating only latitude still validates SA bounds."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        # Send only latitude that's outside SA bounds
        response = client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/address",
            json={"latitude": 0},  # Equator, not in SA
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_COORDINATES"

    def test_single_longitude_update_validates_bounds(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that updating only longitude still validates SA bounds."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        # Send only longitude that's outside SA bounds
        response = client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/address",
            json={"longitude": 0},  # Prime meridian, not in SA
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_COORDINATES"

    def test_valid_single_coordinate_update(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that valid single coordinate update succeeds."""
        gym = create_test_gym(db)
        staff, token = create_test_staff(db, gym, StaffRole.OWNER)

        # Send only latitude within SA bounds
        response = client.put(
            f"{settings.API_V1_STR}/gyms/{gym.id}/address",
            json={"latitude": -26.0},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["latitude"] == -26.0
