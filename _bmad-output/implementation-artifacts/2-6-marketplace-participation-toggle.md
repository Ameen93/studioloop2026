# Story 2.6: Marketplace Participation Toggle

Status: ready-for-dev

## Story

As a **gym owner**,
I want to enable or disable marketplace participation,
So that I can control whether my classes appear on the marketplace.

## Acceptance Criteria

1. **Given** I am on the gym settings page
   **When** I toggle marketplace participation
   **Then** I can enable or disable marketplace for my entire gym

2. **And** when disabled, none of my classes appear in marketplace search

3. **And** when enabled, I can still control individual class marketplace visibility

4. **And** the toggle is stored in `gyms.settings` JSON field

5. **And** existing marketplace bookings are honored even if disabled

## Tasks / Subtasks

- [ ] Task 1: Create marketplace toggle endpoint (AC: #1, #4)
  - [ ] 1.1 Create `PUT /gyms/{gym_id}/settings/marketplace` endpoint
  - [ ] 1.2 Accept `enabled: bool` in request body
  - [ ] 1.3 Store in settings JSON under "marketplace.enabled" key
  - [ ] 1.4 Require owner role only (not manager)

- [ ] Task 2: Update is_marketplace_enabled field (AC: #1, #2)
  - [ ] 2.1 Keep `is_marketplace_enabled` on Gym model as quick-check field
  - [ ] 2.2 Sync settings.marketplace.enabled with is_marketplace_enabled
  - [ ] 2.3 Create utility function `is_gym_marketplace_enabled(gym_id) -> bool`

- [ ] Task 3: Create marketplace status getter (AC: #3)
  - [ ] 3.1 Create `GET /gyms/{gym_id}/settings/marketplace` endpoint
  - [ ] 3.2 Return marketplace enabled status
  - [ ] 3.3 Include info about individual class control

- [ ] Task 4: Document marketplace filtering (AC: #2, #5)
  - [ ] 4.1 Document filter for marketplace search queries
  - [ ] 4.2 Note: Existing bookings honored (no auto-cancel on disable)
  - [ ] 4.3 Integration point for Epic 7 (Marketplace Discovery)

- [ ] Task 5: Add backend tests
  - [ ] 5.1 Test enabling marketplace participation
  - [ ] 5.2 Test disabling marketplace participation
  - [ ] 5.3 Test only owner can toggle (not manager)
  - [ ] 5.4 Test is_marketplace_enabled field syncs
  - [ ] 5.5 Test marketplace status getter

- [ ] Task 6: Regenerate API client
  - [ ] 6.1 Run `pnpm generate:api` in frontend workspace
  - [ ] 6.2 Verify marketplace settings types are generated

## Dev Notes

### Architecture Compliance

- **ARCH-13**: RBAC - Only owner can toggle marketplace (business decision)
- **ARCH-24**: All API/DB fields use `snake_case`
- **ARCH-28**: Standard error response format
- **FR12**: Gym owners can enable/disable marketplace participation

### Settings JSON Structure

```json
{
  "marketplace": {
    "enabled": true,
    "auto_approve_bookings": true,
    "commission_rate": 0.15
  },
  "cancellation_policy": { ... }
}
```

### Marketplace Schema

```python
class MarketplaceSettingsUpdate(SQLModel):
    enabled: bool

class MarketplaceSettingsResponse(SQLModel):
    enabled: bool
    can_control_per_class: bool = True  # Always true
    active_marketplace_bookings: int  # Count of future bookings
```

### Marketplace Filter for Search

```python
def get_marketplace_gyms(session: Session) -> list[UUID]:
    """Get list of gym IDs participating in marketplace."""
    return session.exec(
        select(Gym.id)
        .where(Gym.is_marketplace_enabled == True)
        .where(Gym.is_active == True)
    ).all()
```

### Important: Existing Bookings

When marketplace is disabled:
- New bookings via marketplace are blocked
- Existing future bookings remain valid
- Gym must manually cancel if needed (not automated)

### Dependencies

- Story 2.1: Gym Registration (COMPLETE) - is_marketplace_enabled field exists
- Story 2.5: Cancellation Policy (provides settings JSON pattern)
- Integration point for Epic 7 (Marketplace Discovery)

---

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

