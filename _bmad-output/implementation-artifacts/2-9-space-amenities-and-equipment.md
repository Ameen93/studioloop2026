# Story 2.9: Space Amenities and Equipment

Status: ready-for-dev

## Story

As a **gym owner**,
I want to specify amenities and equipment for each space,
So that staff can choose appropriate spaces for classes.

## Acceptance Criteria

1. **Given** I am editing a space
   **When** I configure amenities and equipment
   **Then** I can select from predefined equipment (mats, bikes, weights, TRX, etc.)

2. **And** I can select from predefined amenities (mirrors, sound system, AC, natural light, etc.)

3. **And** I can add custom equipment/amenities

4. **And** equipment and amenities are stored as arrays in `spaces` table

5. **And** this information is displayed when scheduling classes

## Tasks / Subtasks

- [ ] Task 1: Add amenities/equipment fields to Space model (AC: #4)
  - [ ] 1.1 Add `equipment` JSON array field to Space model
  - [ ] 1.2 Add `amenities` JSON array field to Space model
  - [ ] 1.3 Create Alembic migration for new fields
  - [ ] 1.4 Update SpaceCreate and SpaceUpdate schemas

- [ ] Task 2: Create predefined options endpoints (AC: #1, #2)
  - [ ] 2.1 Create `GET /spaces/equipment-options` to list predefined equipment
  - [ ] 2.2 Create `GET /spaces/amenity-options` to list predefined amenities
  - [ ] 2.3 Define predefined lists as constants

- [ ] Task 3: Update space endpoints for amenities (AC: #1, #2, #3)
  - [ ] 3.1 Accept equipment and amenities arrays in create/update
  - [ ] 3.2 Validate predefined items exist (or allow custom)
  - [ ] 3.3 Store custom items with "custom:" prefix

- [ ] Task 4: Update SpacePublic response (AC: #5)
  - [ ] 4.1 Include equipment and amenities in response
  - [ ] 4.2 Separate predefined from custom items in response

- [ ] Task 5: Add backend tests
  - [ ] 5.1 Test adding predefined equipment
  - [ ] 5.2 Test adding predefined amenities
  - [ ] 5.3 Test adding custom equipment
  - [ ] 5.4 Test adding custom amenities
  - [ ] 5.5 Test equipment/amenities in space response
  - [ ] 5.6 Test predefined options endpoints

- [ ] Task 6: Regenerate API client
  - [ ] 6.1 Run `pnpm generate:api` in frontend workspace
  - [ ] 6.2 Verify equipment/amenity types are generated

## Dev Notes

### Architecture Compliance

- **ARCH-13**: RBAC - Owner/manager can update space amenities
- **ARCH-24**: All API/DB fields use `snake_case`
- **ARCH-28**: Standard error response format
- **FR28**: Gym owners can configure space amenities and equipment

### Predefined Equipment List

```python
PREDEFINED_EQUIPMENT = [
    "yoga_mats",
    "spin_bikes",
    "dumbbells",
    "kettlebells",
    "barbells",
    "weight_plates",
    "resistance_bands",
    "trx_straps",
    "medicine_balls",
    "foam_rollers",
    "yoga_blocks",
    "boxing_bags",
    "battle_ropes",
    "rowing_machines",
    "treadmills",
]
```

### Predefined Amenities List

```python
PREDEFINED_AMENITIES = [
    "mirrors",
    "sound_system",
    "air_conditioning",
    "natural_light",
    "changing_rooms",
    "showers",
    "lockers",
    "water_fountain",
    "tv_screens",
    "microphone",
    "projector",
    "ballet_barre",
    "sprung_floor",
]
```

### Space Model Updates

```python
class Space(GymScopedSoftDeleteModel, SpaceBase, table=True):
    # Existing fields...

    # New fields for amenities/equipment
    equipment: list[str] = Field(
        default=[],
        sa_type=JSON,
        description="List of equipment in this space",
    )
    amenities: list[str] = Field(
        default=[],
        sa_type=JSON,
        description="List of amenities in this space",
    )
```

### Custom Items Convention

Custom items are prefixed with `custom:`:
```python
equipment = ["yoga_mats", "dumbbells", "custom:Pilates reformer machines"]
```

### Space Schema Updates

```python
class SpaceCreate(SpaceBase):
    equipment: list[str] = []
    amenities: list[str] = []

class SpacePublic(SpaceBase):
    id: UUID
    gym_id: UUID
    equipment: list[str]
    amenities: list[str]
    # ... other fields
```

### Dependencies

- Story 2.8: Space Creation and Management (provides base space CRUD)
- Integration point for Epic 5 (space selection for class scheduling)

---

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

