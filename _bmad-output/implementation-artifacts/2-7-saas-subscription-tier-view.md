# Story 2.7: SaaS Subscription Tier View

Status: ready-for-dev

## Story

As a **gym owner**,
I want to view my SaaS subscription details,
So that I understand my plan and limits.

## Acceptance Criteria

1. **Given** I am on the gym settings page
   **When** I view subscription details
   **Then** I can see my current tier (Starter, Growth, Pro)

2. **And** I can see my member limit and current count

3. **And** I can see my staff limit and current count

4. **And** I can see my renewal date

5. **And** I can see a link to upgrade (future payment integration)

6. **And** subscription tier is stored in `gyms.subscription_tier` enum

## Tasks / Subtasks

- [ ] Task 1: Add subscription fields to Gym model (AC: #6)
  - [ ] 1.1 Create `SubscriptionTier` enum (STARTER, GROWTH, PRO)
  - [ ] 1.2 Add `subscription_tier` field to Gym model (default: STARTER)
  - [ ] 1.3 Add `subscription_renewal_date` field (nullable date)
  - [ ] 1.4 Create Alembic migration for subscription fields

- [ ] Task 2: Define tier limits (AC: #2, #3)
  - [ ] 2.1 Create `TIER_LIMITS` config with member/staff limits per tier
  - [ ] 2.2 Starter: 100 members, 5 staff
  - [ ] 2.3 Growth: 500 members, 15 staff
  - [ ] 2.4 Pro: unlimited members, unlimited staff

- [ ] Task 3: Create subscription status endpoint (AC: #1, #2, #3, #4, #5)
  - [ ] 3.1 Create `GET /gyms/{gym_id}/subscription` endpoint
  - [ ] 3.2 Return tier name and limits
  - [ ] 3.3 Calculate current member count (from memberships)
  - [ ] 3.4 Calculate current staff count
  - [ ] 3.5 Return renewal date
  - [ ] 3.6 Include upgrade URL placeholder
  - [ ] 3.7 Require owner/manager role

- [ ] Task 4: Create limit enforcement utilities
  - [ ] 4.1 Create `can_add_member(gym_id) -> tuple[bool, str]`
  - [ ] 4.2 Create `can_add_staff(gym_id) -> tuple[bool, str]`
  - [ ] 4.3 Document integration points for member/staff creation

- [ ] Task 5: Add backend tests
  - [ ] 5.1 Test subscription status returns correct tier
  - [ ] 5.2 Test member count calculation
  - [ ] 5.3 Test staff count calculation
  - [ ] 5.4 Test limit enforcement for each tier
  - [ ] 5.5 Test renewal date display

- [ ] Task 6: Regenerate API client
  - [ ] 6.1 Run `pnpm generate:api` in frontend workspace
  - [ ] 6.2 Verify SubscriptionTier types are generated

## Dev Notes

### Architecture Compliance

- **ARCH-13**: RBAC - Only owner/manager can view subscription
- **ARCH-24**: All API/DB fields use `snake_case`
- **ARCH-27**: UUIDs for all primary keys
- **ARCH-28**: Standard error response format
- **FR13**: Gym owners can view SaaS subscription details

### Subscription Tier Enum

```python
class SubscriptionTier(str, Enum):
    STARTER = "starter"
    GROWTH = "growth"
    PRO = "pro"
```

### Tier Limits Configuration

```python
TIER_LIMITS = {
    SubscriptionTier.STARTER: {
        "member_limit": 100,
        "staff_limit": 5,
        "price_zar": 499,
    },
    SubscriptionTier.GROWTH: {
        "member_limit": 500,
        "staff_limit": 15,
        "price_zar": 999,
    },
    SubscriptionTier.PRO: {
        "member_limit": None,  # Unlimited
        "staff_limit": None,  # Unlimited
        "price_zar": 1999,
    },
}
```

### Subscription Response Schema

```python
class SubscriptionStatusResponse(SQLModel):
    tier: SubscriptionTier
    tier_display_name: str  # "Starter", "Growth", "Pro"

    member_limit: int | None  # None = unlimited
    member_count: int
    member_usage_percent: float | None

    staff_limit: int | None
    staff_count: int
    staff_usage_percent: float | None

    renewal_date: date | None
    upgrade_url: str = "/settings/upgrade"  # Placeholder
```

### Limit Enforcement

```python
def can_add_member(session: Session, gym_id: UUID) -> tuple[bool, str | None]:
    """Check if gym can add another member."""
    gym = session.get(Gym, gym_id)
    limits = TIER_LIMITS[gym.subscription_tier]

    if limits["member_limit"] is None:
        return True, None  # Unlimited

    current_count = get_member_count(session, gym_id)
    if current_count >= limits["member_limit"]:
        return False, f"Member limit ({limits['member_limit']}) reached. Upgrade to add more."
    return True, None
```

### Dependencies

- Story 2.1: Gym Registration (COMPLETE)
- Integration point for Epic 4 (Membership) - member limit check
- Integration point for Epic 3 (Staff Management) - staff limit check

---

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

