# Story 2.10: Space Double-Booking Prevention

Status: ready-for-dev

## Story

As a **system**,
I want to prevent double-booking of spaces,
So that no two classes are scheduled in the same space at the same time.

## Acceptance Criteria

1. **Given** a space with an existing class session
   **When** staff attempts to schedule another class in the same space at overlapping times
   **Then** the system rejects the booking with a clear error message

2. **And** the system suggests alternative available spaces

3. **And** the check considers start_time and end_time of both sessions

4. **And** cancelled sessions do not block new bookings

## Tasks / Subtasks

- [ ] Task 1: Create space availability check utility (AC: #1, #3, #4)
  - [ ] 1.1 Create `is_space_available(space_id, start_time, end_time) -> bool`
  - [ ] 1.2 Query class_sessions table for overlapping time slots
  - [ ] 1.3 Exclude cancelled sessions from overlap check
  - [ ] 1.4 Handle edge cases (back-to-back sessions OK)

- [ ] Task 2: Create available spaces finder (AC: #2)
  - [ ] 2.1 Create `get_available_spaces(gym_id, start_time, end_time) -> list[Space]`
  - [ ] 2.2 Return all active spaces without overlapping sessions
  - [ ] 2.3 Include space details (name, capacity, equipment)

- [ ] Task 3: Create availability check endpoint
  - [ ] 3.1 Create `GET /gyms/{gym_id}/spaces/available` endpoint
  - [ ] 3.2 Accept start_time, end_time query params
  - [ ] 3.3 Return list of available spaces with capacity info

- [ ] Task 4: Create overlap error response (AC: #1, #2)
  - [ ] 4.1 Define `SPACE_NOT_AVAILABLE` error code
  - [ ] 4.2 Include conflicting session details in error
  - [ ] 4.3 Include alternative spaces in error response
  - [ ] 4.4 Document integration point for class scheduling

- [ ] Task 5: Add backend tests
  - [ ] 5.1 Test space available when no sessions exist
  - [ ] 5.2 Test space unavailable with overlapping session
  - [ ] 5.3 Test cancelled sessions don't block bookings
  - [ ] 5.4 Test back-to-back sessions allowed
  - [ ] 5.5 Test get_available_spaces returns correct spaces
  - [ ] 5.6 Test availability endpoint

- [ ] Task 6: Regenerate API client
  - [ ] 6.1 Run `pnpm generate:api` in frontend workspace
  - [ ] 6.2 Verify availability types are generated

## Dev Notes

### Architecture Compliance

- **ARCH-24**: All API/DB fields use `snake_case`
- **ARCH-27**: UUIDs for all primary keys
- **ARCH-28**: Standard error response format with alternatives
- **ARCH-30**: Every gym-scoped query MUST include gym_id filter
- **FR29**: System prevents double-booking of spaces

### Space Availability Check

```python
def is_space_available(
    session: Session,
    space_id: UUID,
    start_time: datetime,
    end_time: datetime,
    exclude_session_id: UUID | None = None,  # For updates
) -> bool:
    """Check if space is available for the given time slot."""
    query = (
        select(ClassSession)
        .where(ClassSession.space_id == space_id)
        .where(ClassSession.status != SessionStatus.CANCELLED)
        .where(
            # Overlap detection: new session overlaps if it starts before existing ends
            # AND ends after existing starts
            and_(
                ClassSession.start_time < end_time,
                ClassSession.end_time > start_time,
            )
        )
    )

    if exclude_session_id:
        query = query.where(ClassSession.id != exclude_session_id)

    return session.exec(query).first() is None
```

### Overlap Detection Logic

Two time ranges overlap if: `start1 < end2 AND end1 > start2`

```
Existing:    |-----|
New case 1:       |-----|  (starts before existing ends) OVERLAP
New case 2:  |-----|       (ends after existing starts) OVERLAP
New case 3:            |-----|  (no overlap, after)
New case 4: |-----|              (no overlap, before)
```

### Get Available Spaces

```python
def get_available_spaces(
    session: Session,
    gym_id: UUID,
    start_time: datetime,
    end_time: datetime,
) -> list[Space]:
    """Get all spaces available for the given time slot."""
    # Get all active spaces for gym
    all_spaces = session.exec(
        select(Space)
        .where(Space.gym_id == gym_id)
        .where(Space.is_active == True)
        .where(Space.is_bookable == True)
    ).all()

    # Filter to available ones
    return [
        space for space in all_spaces
        if is_space_available(session, space.id, start_time, end_time)
    ]
```

### Error Response with Alternatives

```json
{
  "detail": {
    "code": "SPACE_NOT_AVAILABLE",
    "message": "Main Studio is not available at this time",
    "details": {
      "space_id": "uuid",
      "space_name": "Main Studio",
      "conflict": {
        "session_id": "uuid",
        "class_name": "Yoga Flow",
        "start_time": "2024-01-15T10:00:00Z",
        "end_time": "2024-01-15T11:00:00Z"
      },
      "alternatives": [
        {"id": "uuid", "name": "Spin Room", "capacity": 20},
        {"id": "uuid", "name": "Yoga Studio B", "capacity": 15}
      ]
    }
  }
}
```

### Note: ClassSession Model

This story depends on ClassSession model which will be created in Epic 5. For now:
- Create the utility functions with proper typing
- Mock/stub the ClassSession for testing
- Document the integration point

### Dependencies

- Story 2.8: Space Creation and Management (COMPLETE)
- Epic 5: Class Scheduling - ClassSession model (integration point)

---

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

