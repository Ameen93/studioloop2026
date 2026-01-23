# Story 0.8: Create Seed Data Scripts

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want scripts to populate the database with realistic test data,
so that I can test features with meaningful data during development.

## Acceptance Criteria

1. **Given** the database schema is migrated **When** I run `python scripts/seed.py` (or equivalent) **Then** sample gyms are created with realistic SA gym names and locations
2. Sample consumers are created with SA-style names and phone numbers
3. Sample staff members are created with different roles (Owner, Manager, Front Desk, Instructor)
4. Sample membership plans are created (Basic, Premium, Unlimited)
5. Sample class templates are created (Yoga, Spin, HIIT, CrossFit)
6. Sample class sessions are scheduled for the next 14 days
7. Sample bookings exist for testing check-in flows
8. Seed data is idempotent (can be run multiple times safely)
9. A `--reset` flag clears existing seed data before re-seeding

## Tasks / Subtasks

- [x] Task 1: Create seed script infrastructure (AC: #8, #9)
  - [x] Create `backend/scripts/seed.py` entry point script
  - [x] Add CLI argument parsing with `--reset` flag
  - [x] Create `backend/app/seed/` module for seed data logic
  - [x] Create `backend/app/seed/__init__.py` with main `seed_all()` function
  - [x] Implement idempotent seeding pattern (check exists before creating)
  - [x] Implement `--reset` to truncate seed data tables in correct order

- [x] Task 2: Create SA-realistic gym seed data (AC: #1)
  - [x] Create `backend/app/seed/gyms.py` with `seed_gyms()` function
  - [x] Add 3-5 sample gyms with SA-style names:
    - "FitZone Sandton" (Johannesburg)
    - "Oxygen Fitness Cape Town" (Cape Town)
    - "Pure Energy Pretoria" (Pretoria)
    - "The Sweat Box Durban" (Durban)
    - "CrossFit Centurion" (Centurion)
  - [x] Include realistic SA addresses, phone numbers (+27...), coordinates
  - [x] Use existing Gym model from `app/models/gym.py`

- [x] Task 3: Create SA-realistic consumer seed data (AC: #2)
  - [x] Create `backend/app/seed/consumers.py` with `seed_consumers()` function
  - [x] Add 10-20 sample consumers with SA-style names
  - [x] Use SA phone format: +27 xx xxx xxxx
  - [x] Mix of verified/unverified emails
  - [x] Include test consumer: `test@studioloop.com` / `testpassword123`

- [x] Task 4: Create staff seed data (AC: #3)
  - [x] Create `backend/app/seed/staff.py` with `seed_staff()` function
  - [x] **NOTE:** Staff model does not exist yet - this task is DEFERRED
  - [x] Add placeholder comment documenting future staff roles:
    - Owner (gym creator, full access)
    - Manager (scheduling, staff management)
    - Front Desk (check-ins, basic member info)
    - Instructor (own classes only)

- [x] Task 5: Create membership plans seed data (AC: #4)
  - [x] Create `backend/app/seed/membership_plans.py` with `seed_membership_plans()` function
  - [x] **NOTE:** MembershipPlan model does not exist yet - this task is DEFERRED
  - [x] Add placeholder comment documenting future plans:
    - Basic (R299/month, 8 classes)
    - Premium (R499/month, unlimited classes)
    - Unlimited (R699/month, unlimited + priority booking)

- [x] Task 6: Create class templates seed data (AC: #5)
  - [x] Create `backend/app/seed/class_templates.py` with `seed_class_templates()` function
  - [x] **NOTE:** ClassTemplate model does not exist yet - this task is DEFERRED
  - [x] Add placeholder comment documenting future templates:
    - Yoga (60 min, capacity 20)
    - Spin (45 min, capacity 15)
    - HIIT (30 min, capacity 25)
    - CrossFit (60 min, capacity 12)
    - Pilates (55 min, capacity 18)

- [x] Task 7: Create class sessions seed data (AC: #6)
  - [x] Create `backend/app/seed/class_sessions.py` with `seed_class_sessions()` function
  - [x] **NOTE:** ClassSession model does not exist yet - this task is DEFERRED
  - [x] Add placeholder documenting future sessions for next 14 days

- [x] Task 8: Create bookings seed data (AC: #7)
  - [x] Create `backend/app/seed/bookings.py` with `seed_bookings()` function
  - [x] **NOTE:** Booking model does not exist yet - this task is DEFERRED
  - [x] Add placeholder documenting future booking patterns

- [x] Task 9: Create spaces seed data (AVAILABLE - model exists!)
  - [x] Create `backend/app/seed/spaces.py` with `seed_spaces()` function
  - [x] Add 2-4 spaces per gym:
    - "Main Studio" (capacity 30, has mirrors, sound system, AC)
    - "Spin Room" (capacity 20, has sound system, AC)
    - "Yoga Studio" (capacity 25, has mirrors, AC)
    - "CrossFit Box" (capacity 15)
  - [x] Use existing Space model from `app/models/space.py`

- [x] Task 10: Wire up seed orchestration (AC: #8)
  - [x] Create `backend/app/seed/orchestrator.py` to manage seed order
  - [x] Implement dependency-aware seeding (gyms before spaces)
  - [x] Return summary of what was seeded

- [x] Task 11: Add seed documentation and tests
  - [x] Add docstrings to all seed functions
  - [x] Create `backend/tests/seed/test_seed.py` with basic tests
  - [x] Add README section for seed usage

## Dev Notes

### Current Model Availability

| Model | Status | Location | Can Seed? |
|-------|--------|----------|-----------|
| Gym | ✅ EXISTS | `app/models/gym.py` | YES |
| Consumer | ✅ EXISTS | `app/models/consumer.py` | YES |
| Space | ✅ EXISTS | `app/models/space.py` | YES |
| Staff | ❌ NOT YET | Epic 3 | DEFER |
| MembershipPlan | ❌ NOT YET | Epic 4 | DEFER |
| ClassTemplate | ❌ NOT YET | Epic 5 | DEFER |
| ClassSession | ❌ NOT YET | Epic 5 | DEFER |
| Booking | ❌ NOT YET | Epic 6 | DEFER |

**CRITICAL:** Only seed models that exist. Create placeholder modules for future models with clear comments about which epic will create them.

### Idempotent Seeding Pattern

```python
# app/seed/gyms.py - Example pattern
from sqlmodel import Session, select
from app.models import Gym

SEED_GYMS = [
    {"slug": "fitzone-sandton", "name": "FitZone Sandton", ...},
    {"slug": "oxygen-cape-town", "name": "Oxygen Fitness Cape Town", ...},
]

def seed_gyms(session: Session) -> list[Gym]:
    """Seed sample gyms idempotently.

    Returns list of created/existing gyms.
    """
    gyms = []
    for gym_data in SEED_GYMS:
        # Check if already exists (idempotent)
        existing = session.exec(
            select(Gym).where(Gym.slug == gym_data["slug"])
        ).first()

        if existing:
            gyms.append(existing)
            continue

        gym = Gym(**gym_data)
        session.add(gym)
        gyms.append(gym)

    session.commit()
    for gym in gyms:
        session.refresh(gym)
    return gyms
```

### Reset Pattern

```python
# app/seed/reset.py
from sqlmodel import Session, delete
from app.models import Space, Consumer, Gym  # Order matters!

def reset_seed_data(session: Session) -> None:
    """Delete all seed data in dependency order."""
    # Delete children first (foreign key constraints)
    session.exec(delete(Space))
    session.exec(delete(Consumer))  # No FK to Gym, order flexible
    session.exec(delete(Gym))  # Delete parent last
    session.commit()
```

### SA-Realistic Data Examples

**Gym Names:**
- FitZone Sandton, Oxygen Fitness, Pure Energy, The Sweat Box, CrossFit [Area]

**SA Phone Numbers:**
- Format: +27 XX XXX XXXX (mobile: 6/7/8, landline: varies by region)
- Examples: +27 82 123 4567, +27 11 234 5678

**SA Names (diverse):**
- Thandi Nkosi, Pieter van der Merwe, Priya Naidoo, John Smith
- Sipho Dlamini, Fatima Patel, David Botha, Lerato Molefe

**SA Provinces:**
- Gauteng, Western Cape, KwaZulu-Natal, Eastern Cape, Free State
- Mpumalanga, Limpopo, North West, Northern Cape

**SA Cities:**
- Johannesburg, Cape Town, Durban, Pretoria, Port Elizabeth
- Bloemfontein, East London, Polokwane, Nelspruit, Kimberley

### Project Structure After Implementation

```
backend/
├── scripts/
│   └── seed.py              # CLI entry point
├── app/
│   └── seed/
│       ├── __init__.py      # Main seed_all() function
│       ├── orchestrator.py  # Dependency-aware orchestration
│       ├── reset.py         # Reset/truncate logic
│       ├── gyms.py          # Gym seed data
│       ├── consumers.py     # Consumer seed data
│       ├── spaces.py        # Space seed data
│       ├── staff.py         # PLACEHOLDER (Epic 3)
│       ├── membership_plans.py  # PLACEHOLDER (Epic 4)
│       ├── class_templates.py   # PLACEHOLDER (Epic 5)
│       ├── class_sessions.py    # PLACEHOLDER (Epic 5)
│       └── bookings.py      # PLACEHOLDER (Epic 6)
└── tests/
    └── seed/
        ├── __init__.py
        └── test_seed.py     # Basic seed tests
```

### CLI Usage

```bash
# Run seed script
cd backend
python scripts/seed.py

# Run with reset flag (clears existing seed data)
python scripts/seed.py --reset

# Using uv
uv run python scripts/seed.py
uv run python scripts/seed.py --reset
```

### Architecture Compliance

- **ARCH-24**: All seed data uses snake_case for fields
- **ARCH-27**: All IDs are UUIDs (auto-generated by models)
- **Multi-tenancy**: Spaces are properly linked to gyms via gym_id

### Previous Story Intelligence

From Story 0.7 completion notes:
- Models use `BaseModel` with UUID `id`, `created_at`, `updated_at`
- `GymScopedModel` adds `gym_id` foreign key
- `SoftDeleteMixin` adds `is_active`, `deleted_at`
- Repository pattern available but not required for seeding (direct session usage is fine)
- Existing test utilities in `tests/utils/utils.py`: `random_lower_string()`, `random_email()`

### Testing Requirements

1. **Idempotency test**: Run seed twice, verify no duplicates
2. **Reset test**: Run seed, reset, verify tables empty
3. **Data integrity**: Verify FK relationships (spaces -> gyms)
4. **Count verification**: Check expected counts after seeding

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 0.8]
- [Source: _bmad-output/project-context.md#SA-Specific Rules]
- [Source: backend/app/models/gym.py - Gym model definition]
- [Source: backend/app/models/consumer.py - Consumer model definition]
- [Source: backend/app/models/space.py - Space model definition]
- [Source: backend/tests/conftest.py - Test fixtures pattern]
- [Source: backend/tests/utils/utils.py - Random data utilities]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

None

### Completion Notes List

1. **Seed Infrastructure**: Created CLI entry point `scripts/seed.py` with argparse for `--reset` flag. Module `app/seed/` contains orchestration logic with idempotent seeding pattern (check-exists-before-create using slug/email as unique keys).

2. **Gym Seed Data**: Created 5 SA gyms (FitZone Sandton, Oxygen Fitness Cape Town, Pure Energy Pretoria, The Sweat Box Durban, CrossFit Centurion) with realistic addresses, phone numbers (+27 format), provinces, and GPS coordinates.

3. **Consumer Seed Data**: Created 16 consumers with diverse SA names (Zulu, Afrikaans, Indian, English, Sotho, Xhosa backgrounds). Includes test account `test@studioloop.com` with password `testpassword123`. Mix of verified/unverified emails and phones.

4. **Space Seed Data**: Created 14 spaces across 5 gyms with realistic configurations (Main Studio, Spin Room, Yoga Studio, CrossFit Box, HIIT Zone). Each gym has 2-4 spaces based on their focus.

5. **Placeholder Modules**: Created placeholder modules for Staff (Epic 3), MembershipPlan (Epic 4), ClassTemplate (Epic 5), ClassSession (Epic 5), and Booking (Epic 6) with documented seed data structures for future implementation.

6. **Reset Functionality**: Implemented `reset_seed_data()` function that deletes data in reverse dependency order (Spaces → Consumers → Gyms) to respect FK constraints.

7. **Tests**: Created 11 tests covering idempotency (3 tests), count verification (3 tests), data integrity (3 tests), and reset functionality (2 tests). All tests pass.

8. **AC Notes**: AC #3-7 are satisfied with placeholder modules since the underlying models don't exist yet. The placeholders document the exact seed data structure that will be implemented when those models are created in their respective epics.

### File List

**Created:**
- `backend/scripts/seed.py` - CLI entry point script
- `backend/app/seed/__init__.py` - Module exports
- `backend/app/seed/orchestrator.py` - Seed orchestration and reset logic
- `backend/app/seed/gyms.py` - Gym seed data (5 SA gyms)
- `backend/app/seed/consumers.py` - Consumer seed data (16 SA consumers)
- `backend/app/seed/spaces.py` - Space seed data (14 spaces across gyms)
- `backend/app/seed/staff.py` - Staff placeholder (deferred to Epic 3)
- `backend/app/seed/membership_plans.py` - Membership plans placeholder (deferred to Epic 4)
- `backend/app/seed/class_templates.py` - Class templates placeholder (deferred to Epic 5)
- `backend/app/seed/class_sessions.py` - Class sessions placeholder (deferred to Epic 5)
- `backend/app/seed/bookings.py` - Bookings placeholder (deferred to Epic 6)
- `backend/tests/seed/__init__.py` - Test module
- `backend/tests/seed/test_seed.py` - 11 seed tests
