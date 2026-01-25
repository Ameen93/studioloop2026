# Story 2.3: Operating Hours Configuration

Status: ready-for-dev

## Story

As a **gym owner**,
I want to set my gym's operating hours,
So that members know when we're open.

## Acceptance Criteria

1. **Given** I am on the gym settings page
   **When** I configure operating hours
   **Then** I can set open/close times for each day of the week

2. **And** I can mark days as closed

3. **And** I can set different hours for different days

4. **And** operating hours are stored as JSON in `gyms.business_hours`

5. **And** operating hours are displayed on the gym's public profile

## Tasks / Subtasks

- [ ] Task 1: Add business_hours field to Gym model (AC: #4)
  - [ ] 1.1 Add `business_hours` JSON field to Gym model
  - [ ] 1.2 Create Alembic migration for business_hours field
  - [ ] 1.3 Define BusinessHours schema for validation

- [ ] Task 2: Create business hours update endpoint (AC: #1, #2, #3, #4)
  - [ ] 2.1 Create `PUT /gyms/{gym_id}/business-hours` endpoint
  - [ ] 2.2 Accept array of day configurations (day, open_time, close_time, is_closed)
  - [ ] 2.3 Validate time format (HH:MM in 24-hour)
  - [ ] 2.4 Validate open_time < close_time when not closed
  - [ ] 2.5 Require owner/manager role

- [ ] Task 3: Update public profile endpoint (AC: #5)
  - [ ] 3.1 Include business_hours in GymPublic response
  - [ ] 3.2 Format hours for display (e.g., "Mon-Fri: 06:00-21:00")

- [ ] Task 4: Add backend tests
  - [ ] 4.1 Test setting hours for each day
  - [ ] 4.2 Test marking days as closed
  - [ ] 4.3 Test validation rejects invalid times
  - [ ] 4.4 Test public profile includes hours
  - [ ] 4.5 Test unauthorized users cannot update hours

- [ ] Task 5: Regenerate API client
  - [ ] 5.1 Run `pnpm generate:api` in frontend workspace
  - [ ] 5.2 Verify BusinessHours types are generated

## Dev Notes

### Architecture Compliance

- **ARCH-13**: RBAC - Only owner/manager can update operating hours
- **ARCH-24**: All API/DB fields use `snake_case`
- **ARCH-28**: Standard error response format
- **FR9**: Gym owners can configure operating hours

### Business Hours Schema

```python
class DayHours(SQLModel):
    """Hours for a single day of the week."""
    day: str  # monday, tuesday, etc.
    is_closed: bool = False
    open_time: str | None = None  # "06:00" (24-hour format)
    close_time: str | None = None  # "21:00"

class BusinessHoursUpdate(SQLModel):
    """Schema for updating business hours."""
    hours: list[DayHours]  # 7 entries, one per day
```

### JSON Storage Format

```json
{
  "monday": {"open": "06:00", "close": "21:00"},
  "tuesday": {"open": "06:00", "close": "21:00"},
  "wednesday": {"open": "06:00", "close": "21:00"},
  "thursday": {"open": "06:00", "close": "21:00"},
  "friday": {"open": "06:00", "close": "20:00"},
  "saturday": {"open": "08:00", "close": "14:00"},
  "sunday": null
}
```

`null` indicates closed.

### Dependencies

- Story 2.1: Gym Registration (COMPLETE)
- Story 2.2: Gym Profile Configuration (provides base profile endpoints)

---

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

