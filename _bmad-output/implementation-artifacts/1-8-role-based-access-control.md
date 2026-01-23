# Story 1.8: Role-Based Access Control

Status: ready-for-dev

## Story

As a **system**,
I want to enforce role-based permissions,
So that users only access features appropriate to their role.

## Acceptance Criteria

1. **Given** a user with a specific role (consumer, owner, manager, front_desk, instructor)
   **When** they attempt to access an API endpoint
   **Then** the endpoint validates the role from JWT claims

2. **And** unauthorized roles receive 403 Forbidden with error code `FORBIDDEN`

3. **And** gym-scoped endpoints validate `gym_id` claim matches requested resource

4. **And** consumers cannot access gym management endpoints

5. **And** front_desk cannot access owner-only features (billing, staff management)

## Tasks / Subtasks

- [ ] Task 1: Create role-checking dependencies (AC: #1, #2)
  - [ ] 1.1 Create `RoleChecker` class with `__call__` method for FastAPI dependency injection
  - [ ] 1.2 Accept list of allowed roles in constructor
  - [ ] 1.3 Extract role from JWT `token_data.role` claim
  - [ ] 1.4 Raise 403 `FORBIDDEN` if role not in allowed list
  - [ ] 1.5 Create convenience dependencies: `RequireOwner`, `RequireManager`, `RequireStaff`

- [ ] Task 2: Create gym-scoped access validation dependency (AC: #3)
  - [ ] 2.1 Create `get_current_staff_for_gym` dependency
  - [ ] 2.2 Extract `gym_id` from JWT claims
  - [ ] 2.3 Compare JWT `gym_id` with path parameter `gym_id`
  - [ ] 2.4 Raise 403 `FORBIDDEN` if gym_id mismatch
  - [ ] 2.5 Create `StaffGymDep` annotated type for use in routes

- [ ] Task 3: Create role hierarchy utilities (AC: #5)
  - [ ] 3.1 Define role hierarchy: OWNER > MANAGER > FRONT_DESK / INSTRUCTOR
  - [ ] 3.2 Create `has_permission` function to check role hierarchy
  - [ ] 3.3 Create `RequireOwnerOrManager` dependency for elevated operations

- [ ] Task 4: Update existing staff routes with role guards (AC: #4, #5)
  - [ ] 4.1 Add role guards to staff auth routes (no changes needed - login is public)
  - [ ] 4.2 Document which routes will need protection in future epics

- [ ] Task 5: Create protected route examples for testing (AC: #1-5)
  - [ ] 5.1 Create example routes demonstrating role-based access
  - [ ] 5.2 Owner-only route example
  - [ ] 5.3 Manager-or-above route example
  - [ ] 5.4 Any-staff route example

- [ ] Task 6: Add backend tests for RBAC (AC: #1-5)
  - [ ] 6.1 Test RoleChecker allows valid roles
  - [ ] 6.2 Test RoleChecker rejects unauthorized roles with 403
  - [ ] 6.3 Test gym_id validation passes for matching gym
  - [ ] 6.4 Test gym_id validation fails for mismatched gym with 403
  - [ ] 6.5 Test consumer token cannot access staff routes
  - [ ] 6.6 Test front_desk cannot access owner-only routes
  - [ ] 6.7 Test role hierarchy (manager can do front_desk tasks)

## Dev Notes

### Architecture Compliance

- **ARCH-13**: RBAC with role claims in JWT (Owner, Manager, Front Desk, Instructor, Consumer)
- **ARCH-10**: Custom JWT (FastAPI native) for authentication
- **ARCH-28**: Standard error response format with code, message, details
- **Multi-tenancy**: Row-level security via gym_id validation

### Existing Code to Reuse

**StaffRole enum (`backend/app/models/staff.py:24-34`):**
```python
class StaffRole(str, Enum):
    """Staff roles per ARCH-13 RBAC.

    Hierarchy: owner > manager > front_desk / instructor
    """
    OWNER = "owner"
    MANAGER = "manager"
    FRONT_DESK = "front_desk"
    INSTRUCTOR = "instructor"
```

**UserRole enum (`backend/app/models/consumer.py:18-30`):**
```python
class UserRole(str, Enum):
    """User roles for platform access control (ARCH-13)."""
    CONSUMER = "consumer"
    OWNER = "owner"
    MANAGER = "manager"
    FRONT_DESK = "front_desk"
    INSTRUCTOR = "instructor"
```

**TokenPayload already has role and gym_id (`backend/app/models_legacy.py:108-112`):**
```python
class TokenPayload(SQLModel):
    sub: str | None = None
    type: str | None = None  # "access" or "refresh"
    role: str | None = None  # Staff role (owner, manager, front_desk, instructor)
    gym_id: str | None = None  # Gym ID for tenant context (staff tokens only)
    token_version: int | None = None
```

**Existing CurrentStaff dependency (`backend/app/api/deps.py:134-196`):**
- Validates JWT and returns Staff model
- Already decodes `token_data` with role and gym_id

**GymDep has TODO for access validation (`backend/app/api/deps.py:254-259`):**
```python
# TODO: Implement user-gym access validation
# This will check if the user has a role (staff, owner) at this gym
```

### Implementation Patterns

**RoleChecker dependency class pattern:**
```python
from fastapi import Depends, HTTPException, status
from typing import Annotated

class RoleChecker:
    """FastAPI dependency for role-based access control.

    Usage:
        @router.get("/admin", dependencies=[Depends(RoleChecker(["owner", "manager"]))])
        def admin_route(): ...

        # Or as a parameter dependency:
        @router.get("/admin")
        def admin_route(
            _role_check: Annotated[None, Depends(RoleChecker(["owner"]))]
        ): ...
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        current_staff: CurrentStaff,
    ) -> None:
        """Check if current staff has required role.

        Raises:
            HTTPException: 403 FORBIDDEN if role not allowed
        """
        if current_staff.role.value not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "Insufficient permissions",
                    "details": {"required_roles": self.allowed_roles},
                },
            )


# Convenience dependencies
RequireOwner = Depends(RoleChecker(["owner"]))
RequireManager = Depends(RoleChecker(["owner", "manager"]))
RequireStaff = Depends(RoleChecker(["owner", "manager", "front_desk", "instructor"]))
```

**Gym-scoped access validation pattern:**
```python
def get_current_staff_for_gym(
    gym_id: Annotated[UUID, Path(description="Gym ID")],
    current_staff: CurrentStaff,
) -> Staff:
    """Validate staff member has access to the specified gym.

    Compares gym_id from path with staff's gym_id to ensure
    tenant isolation.

    Args:
        gym_id: UUID from path parameter
        current_staff: Authenticated staff from JWT

    Returns:
        Staff model if authorized

    Raises:
        HTTPException: 403 FORBIDDEN if gym_id mismatch
    """
    if str(current_staff.gym_id) != str(gym_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Access denied to this gym",
                "details": {},
            },
        )
    return current_staff


StaffGymDep = Annotated[Staff, Depends(get_current_staff_for_gym)]
```

**Role hierarchy pattern:**
```python
# Role hierarchy for permission inheritance
ROLE_HIERARCHY = {
    "owner": 4,
    "manager": 3,
    "front_desk": 2,
    "instructor": 2,  # Same level as front_desk (peer roles)
    "consumer": 1,
}


def has_permission(user_role: str, required_role: str) -> bool:
    """Check if user role has at least required permission level.

    Args:
        user_role: The role the user has
        required_role: The minimum role required

    Returns:
        True if user_role >= required_role in hierarchy
    """
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)
```

### Error Response Format

All RBAC errors use standard format (ARCH-28):
```json
{
  "detail": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions",
    "details": {"required_roles": ["owner", "manager"]}
  }
}
```

### Testing Patterns

```python
class TestRoleBasedAccess:
    """Tests for RBAC dependencies."""

    def test_owner_can_access_owner_route(self, client, db: Session):
        """Test owner role can access owner-only routes."""
        staff, token = create_staff_with_token(db, role=StaffRole.OWNER)

        response = client.get(
            f"{settings.API_V1_STR}/gyms/{staff.gym_id}/admin/settings",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_front_desk_cannot_access_owner_route(self, client, db: Session):
        """Test front_desk role cannot access owner-only routes."""
        staff, token = create_staff_with_token(db, role=StaffRole.FRONT_DESK)

        response = client.get(
            f"{settings.API_V1_STR}/gyms/{staff.gym_id}/admin/settings",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "FORBIDDEN"

    def test_staff_cannot_access_other_gym(self, client, db: Session):
        """Test staff cannot access routes for a different gym."""
        staff, token = create_staff_with_token(db)
        other_gym = create_gym(db)  # Different gym

        response = client.get(
            f"{settings.API_V1_STR}/gyms/{other_gym.id}/members",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "FORBIDDEN"

    def test_consumer_cannot_access_staff_route(self, client, db: Session):
        """Test consumer token cannot access staff-only routes."""
        consumer, token = create_consumer_with_token(db)
        gym = create_gym(db)

        response = client.get(
            f"{settings.API_V1_STR}/gyms/{gym.id}/members",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should fail at CurrentStaff dependency (staff not found)
        assert response.status_code == 401

    def test_manager_can_do_front_desk_tasks(self, client, db: Session):
        """Test manager role inherits front_desk permissions."""
        staff, token = create_staff_with_token(db, role=StaffRole.MANAGER)

        response = client.post(
            f"{settings.API_V1_STR}/gyms/{staff.gym_id}/check-ins",
            headers={"Authorization": f"Bearer {token}"},
            json={"consumer_id": "..."},
        )

        # Manager should be able to do front_desk tasks
        # (actual endpoint doesn't exist yet, this is pattern example)
        assert response.status_code in [200, 201, 404]  # 404 if endpoint not implemented
```

### Previous Story Intelligence

From Story 1.3 (Staff Email Login):
- `CurrentStaff` dependency pattern
- Staff JWT includes `role` and `gym_id` claims
- Token creation with staff-specific claims

From Story 1.7 (POPIA Account Deletion):
- 401 vs 403 distinction (401 = auth failure, 403 = authorized but forbidden)
- Standard error format with code, message, details

### What NOT to Do

- **DO NOT** create actual protected routes for gym management (those come in Epic 2+)
- **DO NOT** modify existing consumer routes (they use different auth flow)
- **DO NOT** implement platform_admin role (not in current scope)
- **DO NOT** hard-code role checks inline - always use dependencies
- **DO NOT** expose internal role hierarchy details in error messages
- **DO NOT** allow any bypass of gym_id validation

### File Structure

Files to create/modify:
```
backend/
├── app/
│   └── api/
│       ├── deps.py              # UPDATE: Add RBAC dependencies
│       └── routes/
│           └── rbac_examples.py # NEW: Example protected routes for testing
└── tests/api/
    └── test_rbac.py             # NEW: RBAC tests
```

### Dependencies on Previous Stories

- Story 1-3: Staff Email Login (DONE) - Staff JWT with role/gym_id claims
- Story 0-7: Multi-tenancy patterns (DONE) - Gym-scoped models

### Project Context Reference

Key patterns from `project-context.md` (if exists):
- All dependencies should use Annotated type hints
- Error responses follow ARCH-28 format
- Staff routes are gym-scoped, consumer routes are platform-scoped

### References

- [Source: epics.md#Story 1.8 - Role-Based Access Control]
- [Source: architecture.md - ARCH-13 RBAC role claims]
- [Source: backend/app/models/staff.py - StaffRole enum]
- [Source: backend/app/models/consumer.py - UserRole enum]
- [Source: backend/app/api/deps.py - CurrentStaff dependency]
- [Source: backend/app/models_legacy.py - TokenPayload with role/gym_id]

---

## QA Checklist

### Role Validation Tests

- [ ] **RoleChecker dependency**
  - [ ] Owner can access owner-only routes (200)
  - [ ] Manager can access manager-or-above routes (200)
  - [ ] Front desk cannot access owner-only routes (403 FORBIDDEN)
  - [ ] Instructor cannot access manager routes (403 FORBIDDEN)
  - [ ] Error response includes `required_roles` in details

### Gym-Scoped Access Tests

- [ ] **StaffGymDep dependency**
  - [ ] Staff can access their own gym's routes (200)
  - [ ] Staff cannot access other gym's routes (403 FORBIDDEN)
  - [ ] gym_id in JWT is validated against path parameter
  - [ ] Error message does not leak gym details

### Cross-Role Tests

- [ ] **Consumer vs Staff isolation**
  - [ ] Consumer token cannot access staff routes (401 INVALID_TOKEN)
  - [ ] Staff token cannot access consumer-only routes (if any exist)

### Role Hierarchy Tests

- [ ] **Permission inheritance**
  - [ ] Owner can do manager tasks
  - [ ] Manager can do front_desk tasks
  - [ ] Front desk cannot do manager tasks
  - [ ] Instructor cannot do front_desk tasks (peer roles, no inheritance)

---

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

