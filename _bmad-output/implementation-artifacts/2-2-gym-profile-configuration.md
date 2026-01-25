# Story 2.2: Gym Profile Configuration

Status: ready-for-dev

## Story

As a **gym owner**,
I want to configure my gym's public profile,
So that consumers can learn about my gym.

## Acceptance Criteria

1. **Given** I am logged in as a gym owner
   **When** I navigate to gym profile settings
   **Then** I can set gym name, description, and tagline

2. **And** I can upload a logo and cover photos (gallery)

3. **And** I can set the gym address with map location (lat/lng via PostGIS)

4. **And** I can add contact email and phone number

5. **And** changes are saved and visible on the gym's public profile

6. **And** photos are stored and served via CDN

## Tasks / Subtasks

- [ ] Task 1: Create gym profile update endpoint (AC: #1, #4, #5)
  - [ ] 1.1 Create `PUT /gyms/{gym_id}/profile` endpoint in `app/api/routes/gyms.py`
  - [ ] 1.2 Add `tagline` field to Gym model (max 200 chars)
  - [ ] 1.3 Create Alembic migration for tagline field
  - [ ] 1.4 Validate gym ownership via Staff role check
  - [ ] 1.5 Return updated GymPublic response

- [ ] Task 2: Create gym address update endpoint (AC: #3)
  - [ ] 2.1 Create `PUT /gyms/{gym_id}/address` endpoint
  - [ ] 2.2 Accept address fields + lat/lng coordinates
  - [ ] 2.3 Validate coordinates are within reasonable SA bounds
  - [ ] 2.4 Update address fields in Gym model

- [ ] Task 3: Create photo upload endpoints (AC: #2, #6)
  - [ ] 3.1 Create `POST /gyms/{gym_id}/logo` endpoint for logo upload
  - [ ] 3.2 Create `POST /gyms/{gym_id}/photos` endpoint for gallery photos
  - [ ] 3.3 Add `logo_url` and `photo_urls` (JSON array) fields to Gym model
  - [ ] 3.4 Create Alembic migration for photo fields
  - [ ] 3.5 Store photos locally for now (CDN integration deferred)
  - [ ] 3.6 Validate file types (jpg, png, webp) and size limits (5MB)

- [ ] Task 4: Create gym public profile endpoint (AC: #5)
  - [ ] 4.1 Create `GET /gyms/{slug}` public endpoint (no auth required)
  - [ ] 4.2 Return GymPublic with all profile fields
  - [ ] 4.3 Include photo URLs in response

- [ ] Task 5: Add backend tests
  - [ ] 5.1 Test profile update requires owner/manager role
  - [ ] 5.2 Test address update with valid coordinates
  - [ ] 5.3 Test photo upload validates file type and size
  - [ ] 5.4 Test public profile endpoint returns correct data
  - [ ] 5.5 Test unauthorized users cannot update profile

- [ ] Task 6: Regenerate API client
  - [ ] 6.1 Run `pnpm generate:api` in frontend workspace
  - [ ] 6.2 Verify new gym profile types are generated

## Dev Notes

### Architecture Compliance

- **ARCH-13**: RBAC - Only owner/manager can update gym profile
- **ARCH-24**: All API/DB fields use `snake_case`
- **ARCH-27**: UUIDs for all primary keys
- **ARCH-28**: Standard error response format with code, message, details
- **ARCH-30**: Every gym-scoped query MUST include gym_id filter
- **FR8**: Gym owners can set up gym profile (name, description, logo, photos)

### Current Codebase State

**Gym model EXISTS at `backend/app/models/gym.py`:**
```python
class Gym(SoftDeleteMixin, BaseModel, GymBase, table=True):
    # Has: name, slug, description, is_marketplace_enabled
    # Has: contact_email, contact_phone (from Story 2.1)
    # Has: address_line1, address_line2, city, province, postal_code, country
    # Has: latitude, longitude
    # Missing: tagline, logo_url, photo_urls
```

**GymUpdate schema already exists** - can be extended for profile updates.

### Critical Implementation Details

#### Photo Storage Strategy

For MVP, store photos locally:
```python
# Upload to: /uploads/gyms/{gym_id}/logo.{ext}
# Upload to: /uploads/gyms/{gym_id}/photos/{uuid}.{ext}
```

CDN integration deferred - just return local file URLs for now.

#### Authorization Check

```python
def require_gym_role(
    session: SessionDep,
    current_staff: Staff,  # From JWT
    gym_id: UUID,
    allowed_roles: list[StaffRole] = [StaffRole.OWNER, StaffRole.MANAGER]
) -> Gym:
    """Verify staff has required role for gym operations."""
    if current_staff.gym_id != gym_id:
        raise HTTPException(403, detail={"code": "FORBIDDEN", ...})
    if current_staff.role not in allowed_roles:
        raise HTTPException(403, detail={"code": "INSUFFICIENT_PERMISSIONS", ...})
    return session.get(Gym, gym_id)
```

### Dependencies

- Story 2.1: Gym Registration (COMPLETE) - Gym model exists with basic fields

---

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

