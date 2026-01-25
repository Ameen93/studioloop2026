# Story 2.5: Cancellation Policy Configuration

Status: ready-for-dev

## Story

As a **gym owner**,
I want to set my gym's cancellation policy,
So that members understand the rules for cancelling bookings.

## Acceptance Criteria

1. **Given** I am on the gym settings page
   **When** I configure cancellation policy
   **Then** I can set the cancellation window (e.g., 2, 6, 12, 24 hours before class)

2. **And** I can set the no-show penalty (none, credit lost, fee)

3. **And** the policy is displayed on class detail screens before booking

4. **And** the policy is enforced when consumers attempt to cancel

5. **And** settings are stored in `gyms.settings` JSON field

## Tasks / Subtasks

- [ ] Task 1: Add settings JSON field to Gym model (AC: #5)
  - [ ] 1.1 Add `settings` JSON field to Gym model
  - [ ] 1.2 Create Alembic migration for settings field
  - [ ] 1.3 Define GymSettings schema for validation

- [ ] Task 2: Create cancellation policy update endpoint (AC: #1, #2, #5)
  - [ ] 2.1 Create `PUT /gyms/{gym_id}/settings/cancellation-policy` endpoint
  - [ ] 2.2 Accept cancellation_window_hours (enum: 2, 6, 12, 24)
  - [ ] 2.3 Accept no_show_penalty (enum: none, credit_lost, fee)
  - [ ] 2.4 Store in settings JSON under "cancellation_policy" key
  - [ ] 2.5 Require owner/manager role

- [ ] Task 3: Create cancellation policy getter (AC: #3)
  - [ ] 3.1 Create `GET /gyms/{gym_id}/settings/cancellation-policy` endpoint
  - [ ] 3.2 Return CancellationPolicyResponse with window and penalty
  - [ ] 3.3 Include default values if not set

- [ ] Task 4: Create policy enforcement utility (AC: #4)
  - [ ] 4.1 Create `can_cancel_booking(gym_id, booking_time) -> tuple[bool, str]`
  - [ ] 4.2 Returns (True, None) if cancellation allowed
  - [ ] 4.3 Returns (False, "Too late to cancel...") if outside window
  - [ ] 4.4 Document integration point for booking cancellation (Epic 6)

- [ ] Task 5: Add backend tests
  - [ ] 5.1 Test setting cancellation window
  - [ ] 5.2 Test setting no-show penalty
  - [ ] 5.3 Test policy getter returns correct values
  - [ ] 5.4 Test can_cancel_booking within window
  - [ ] 5.5 Test can_cancel_booking outside window
  - [ ] 5.6 Test default values when not configured

- [ ] Task 6: Regenerate API client
  - [ ] 6.1 Run `pnpm generate:api` in frontend workspace
  - [ ] 6.2 Verify CancellationPolicy types are generated

## Dev Notes

### Architecture Compliance

- **ARCH-13**: RBAC - Only owner/manager can update cancellation policy
- **ARCH-24**: All API/DB fields use `snake_case`
- **ARCH-28**: Standard error response format
- **FR11**: Gym owners can set cancellation policies

### Settings JSON Structure

```json
{
  "cancellation_policy": {
    "window_hours": 24,
    "no_show_penalty": "credit_lost"
  },
  "marketplace": {
    "enabled": true
  }
}
```

### Cancellation Policy Schema

```python
class CancellationWindowHours(str, Enum):
    TWO = "2"
    SIX = "6"
    TWELVE = "12"
    TWENTY_FOUR = "24"

class NoShowPenalty(str, Enum):
    NONE = "none"
    CREDIT_LOST = "credit_lost"
    FEE = "fee"

class CancellationPolicyUpdate(SQLModel):
    window_hours: CancellationWindowHours = CancellationWindowHours.TWENTY_FOUR
    no_show_penalty: NoShowPenalty = NoShowPenalty.NONE

class CancellationPolicyResponse(SQLModel):
    window_hours: int
    no_show_penalty: str
    description: str  # Human-readable policy text
```

### Policy Enforcement

```python
def can_cancel_booking(
    session: Session,
    gym_id: UUID,
    class_start_time: datetime
) -> tuple[bool, str | None]:
    """Check if booking can be cancelled based on gym policy."""
    gym = session.get(Gym, gym_id)
    policy = gym.settings.get("cancellation_policy", {})
    window_hours = policy.get("window_hours", 24)

    cutoff = class_start_time - timedelta(hours=window_hours)
    if datetime.utcnow() > cutoff:
        return False, f"Cancellation window closed {window_hours} hours before class"
    return True, None
```

### Dependencies

- Story 2.1: Gym Registration (COMPLETE)
- Integration point for Story 6.3 (booking cancellation)

---

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

