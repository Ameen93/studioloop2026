# Story 2.8: Space Creation and Management

Status: ready-for-dev

## Story

As a **gym owner**,
I want to create and manage spaces (rooms/studios),
So that I can schedule classes in specific locations.

## Acceptance Criteria

1. **Given** I am on the spaces management page
   **When** I create a new space
   **Then** I can enter name, capacity, and description

2. **And** a `spaces` table record is created with `gym_id` foreign key

3. **And** I can view a list of all spaces for my gym

4. **And** I can edit existing spaces

5. **And** I can deactivate (soft delete) spaces that are no longer used

6. **And** deactivated spaces are not available for new class scheduling

## Tasks / Subtasks

- [ ] Task 1: Create Space CRUD endpoints (AC: #1, #2, #3, #4, #5)
  - [ ] 1.1 Create `POST /gyms/{gym_id}/spaces` to create space
  - [ ] 1.2 Create `GET /gyms/{gym_id}/spaces` to list spaces
  - [ ] 1.3 Create `GET /gyms/{gym_id}/spaces/{space_id}` to get single space
  - [ ] 1.4 Create `PUT /gyms/{gym_id}/spaces/{space_id}` to update space
  - [ ] 1.5 Create `DELETE /gyms/{gym_id}/spaces/{space_id}` to soft delete
  - [ ] 1.6 Require owner/manager role for all mutations

- [ ] Task 2: Implement space listing with filters (AC: #3, #6)
  - [ ] 2.1 Support `include_inactive` query param (default: false)
  - [ ] 2.2 Sort by name alphabetically
  - [ ] 2.3 Include is_active status in response

- [ ] Task 3: Create active spaces utility (AC: #6)
  - [ ] 3.1 Create `get_active_spaces(gym_id) -> list[Space]`
  - [ ] 3.2 Used by class scheduling to show available spaces
  - [ ] 3.3 Document integration point for Epic 5

- [ ] Task 4: Add backend tests
  - [ ] 4.1 Test creating space with required fields
  - [ ] 4.2 Test listing spaces for gym
  - [ ] 4.3 Test editing space
  - [ ] 4.4 Test soft deleting space
  - [ ] 4.5 Test soft deleted spaces excluded by default
  - [ ] 4.6 Test include_inactive shows all spaces
  - [ ] 4.7 Test gym isolation (can't see other gym's spaces)

- [ ] Task 5: Regenerate API client
  - [ ] 5.1 Run `pnpm generate:api` in frontend workspace
  - [ ] 5.2 Verify Space types are generated

## Dev Notes

### Architecture Compliance

- **ARCH-13**: RBAC - Owner/manager can manage spaces
- **ARCH-24**: All API/DB fields use `snake_case`
- **ARCH-27**: UUIDs for all primary keys
- **ARCH-28**: Standard error response format
- **ARCH-30**: Every gym-scoped query MUST include gym_id filter
- **FR27**: Gym owners can create and manage spaces

### Current Codebase State

**Space model EXISTS at `backend/app/models/space.py`:**
```python
class Space(GymScopedSoftDeleteModel, SpaceBase, table=True):
    __tablename__ = "spaces"

    # Has: name, description, capacity
    # Has: floor_area_sqm, has_mirrors, has_sound_system, has_air_conditioning
    # Has: is_bookable, is_active (from SoftDeleteMixin)
    # Has: gym_id (from GymScopedModel)
```

**SpaceCreate, SpaceUpdate, SpacePublic schemas already exist.**

### Space Routes File

Create `backend/app/api/routes/spaces.py`:

```python
router = APIRouter(prefix="/gyms/{gym_id}/spaces", tags=["spaces"])

@router.post("/", response_model=SpacePublic, status_code=201)
def create_space(
    gym_id: UUID,
    space_data: SpaceCreate,
    session: SessionDep,
    current_staff: CurrentStaffDep,
) -> SpacePublic:
    """Create a new space in the gym."""
    require_gym_role(current_staff, gym_id, [StaffRole.OWNER, StaffRole.MANAGER])
    space = Space(**space_data.model_dump(), gym_id=gym_id)
    session.add(space)
    session.commit()
    session.refresh(space)
    return space
```

### Gym Isolation

All space queries MUST include gym_id filter:

```python
@router.get("/", response_model=list[SpacePublic])
def list_spaces(
    gym_id: UUID,
    session: SessionDep,
    current_staff: CurrentStaffDep,
    include_inactive: bool = False,
) -> list[SpacePublic]:
    query = select(Space).where(Space.gym_id == gym_id)
    if not include_inactive:
        query = query.where(Space.is_active == True)
    return session.exec(query.order_by(Space.name)).all()
```

### Dependencies

- Story 2.1: Gym Registration (COMPLETE)
- Story 0.7: Multi-tenancy patterns (COMPLETE) - GymScopedModel exists
- Integration point for Epic 5 (Class Scheduling)

---

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

