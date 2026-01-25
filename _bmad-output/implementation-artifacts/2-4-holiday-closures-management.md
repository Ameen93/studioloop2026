# Story 2.4: Holiday Closures Management

Status: ready-for-dev

## Story

As a **gym owner**,
I want to set holiday closures,
So that members know when we're closed for special dates.

## Acceptance Criteria

1. **Given** I am on the gym settings page
   **When** I add a holiday closure
   **Then** I can select a date and optionally a reason (e.g., "Christmas Day")

2. **And** I can add multiple closures

3. **And** I can remove existing closures

4. **And** closures are stored in a `gym_closures` table

5. **And** classes cannot be scheduled on closure dates

6. **And** closures are displayed on the gym's public profile

## Tasks / Subtasks

- [ ] Task 1: Create GymClosure model (AC: #4)
  - [ ] 1.1 Create `GymClosure` model in `app/models/gym_closure.py`
  - [ ] 1.2 Fields: id, gym_id, closure_date, reason, created_at
  - [ ] 1.3 Extend GymScopedModel for tenant isolation
  - [ ] 1.4 Create Alembic migration for gym_closures table
  - [ ] 1.5 Add unique constraint on (gym_id, closure_date)

- [ ] Task 2: Create closure CRUD endpoints (AC: #1, #2, #3)
  - [ ] 2.1 Create `POST /gyms/{gym_id}/closures` to add closure
  - [ ] 2.2 Create `GET /gyms/{gym_id}/closures` to list closures
  - [ ] 2.3 Create `DELETE /gyms/{gym_id}/closures/{closure_id}` to remove
  - [ ] 2.4 Validate closure_date is in the future
  - [ ] 2.5 Require owner/manager role

- [ ] Task 3: Add closure validation for class scheduling (AC: #5)
  - [ ] 3.1 Create utility function `is_gym_closed(gym_id, date) -> bool`
  - [ ] 3.2 Export function for use in class scheduling (Epic 5)
  - [ ] 3.3 Document integration point for class creation

- [ ] Task 4: Update public profile endpoint (AC: #6)
  - [ ] 4.1 Add upcoming closures to GymPublic response
  - [ ] 4.2 Only include closures in next 90 days
  - [ ] 4.3 Order by date ascending

- [ ] Task 5: Add backend tests
  - [ ] 5.1 Test adding closure with date and reason
  - [ ] 5.2 Test adding multiple closures
  - [ ] 5.3 Test removing closure
  - [ ] 5.4 Test duplicate date rejection
  - [ ] 5.5 Test past date rejection
  - [ ] 5.6 Test is_gym_closed utility function
  - [ ] 5.7 Test public profile includes upcoming closures

- [ ] Task 6: Regenerate API client
  - [ ] 6.1 Run `pnpm generate:api` in frontend workspace
  - [ ] 6.2 Verify GymClosure types are generated

## Dev Notes

### Architecture Compliance

- **ARCH-13**: RBAC - Only owner/manager can manage closures
- **ARCH-24**: All API/DB fields use `snake_case`
- **ARCH-27**: UUIDs for all primary keys
- **ARCH-28**: Standard error response format
- **ARCH-30**: Every gym-scoped query MUST include gym_id filter
- **FR10**: Gym owners can manage holiday closures

### GymClosure Model

```python
class GymClosure(GymScopedSoftDeleteModel, table=True):
    """Holiday closure for a gym."""
    __tablename__ = "gym_closures"

    closure_date: date = Field(index=True)
    reason: str | None = Field(default=None, max_length=255)

    __table_args__ = (
        UniqueConstraint("gym_id", "closure_date", name="uq_gym_closure_date"),
    )
```

### Closure Utility Function

```python
def is_gym_closed(session: Session, gym_id: UUID, check_date: date) -> bool:
    """Check if gym is closed on a specific date."""
    closure = session.exec(
        select(GymClosure)
        .where(GymClosure.gym_id == gym_id)
        .where(GymClosure.closure_date == check_date)
        .where(GymClosure.is_active == True)
    ).first()
    return closure is not None
```

### Dependencies

- Story 2.1: Gym Registration (COMPLETE)
- Integration point for Story 5.2 (class scheduling)

---

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

