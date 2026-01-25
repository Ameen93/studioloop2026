# Story 2.11: Member Data Spreadsheet Import

Status: ready-for-dev

## Story

As a **gym owner**,
I want to import my existing members from a spreadsheet,
So that I can migrate to StudioLoop without manually entering each member.

## Acceptance Criteria

1. **Given** I have a CSV/Excel file with member data
   **When** I upload the file on the import page
   **Then** the system parses the file and shows a preview of detected members

2. **And** I can map columns to fields (name, email, phone, membership tier)

3. **And** I can review and confirm the import

4. **And** consumer accounts are created for each member (pending email verification)

5. **And** memberships are created linking consumers to my gym

6. **And** duplicate emails are flagged for manual review

7. **And** import results show success/error counts

## Tasks / Subtasks

- [ ] Task 1: Create import file upload endpoint (AC: #1)
  - [ ] 1.1 Create `POST /gyms/{gym_id}/members/import/upload` endpoint
  - [ ] 1.2 Accept CSV or XLSX file upload
  - [ ] 1.3 Parse file and extract headers
  - [ ] 1.4 Return preview of first 5 rows + detected columns
  - [ ] 1.5 Store file temporarily for mapping step

- [ ] Task 2: Create column mapping endpoint (AC: #2)
  - [ ] 2.1 Create `POST /gyms/{gym_id}/members/import/map` endpoint
  - [ ] 2.2 Accept mapping: {column_name: field_name}
  - [ ] 2.3 Required fields: email, first_name, last_name
  - [ ] 2.4 Optional fields: phone, membership_tier
  - [ ] 2.5 Validate all required fields are mapped

- [ ] Task 3: Create import preview endpoint (AC: #3, #6)
  - [ ] 3.1 Create `GET /gyms/{gym_id}/members/import/preview` endpoint
  - [ ] 3.2 Apply mapping to all rows
  - [ ] 3.3 Validate each row (email format, required fields)
  - [ ] 3.4 Check for duplicate emails (within file and in DB)
  - [ ] 3.5 Return preview with validation status per row

- [ ] Task 4: Create import confirmation endpoint (AC: #4, #5, #7)
  - [ ] 4.1 Create `POST /gyms/{gym_id}/members/import/confirm` endpoint
  - [ ] 4.2 Create Consumer records for valid rows
  - [ ] 4.3 Create GymMembership linking Consumer to Gym
  - [ ] 4.4 Skip duplicate emails (flag for manual review)
  - [ ] 4.5 Return import results (success/error counts)
  - [ ] 4.6 Require owner role only

- [ ] Task 5: Create GymMembership model (AC: #5)
  - [ ] 5.1 Create `GymMembership` model in `app/models/gym_membership.py`
  - [ ] 5.2 Fields: id, gym_id, consumer_id, status, created_at
  - [ ] 5.3 Create Alembic migration for gym_memberships table
  - [ ] 5.4 Unique constraint on (gym_id, consumer_id)

- [ ] Task 6: Add backend tests
  - [ ] 6.1 Test CSV file upload and parsing
  - [ ] 6.2 Test XLSX file upload and parsing
  - [ ] 6.3 Test column mapping validation
  - [ ] 6.4 Test preview with valid data
  - [ ] 6.5 Test preview flags duplicate emails
  - [ ] 6.6 Test import creates Consumer and GymMembership records
  - [ ] 6.7 Test import skips duplicates
  - [ ] 6.8 Test import results counts

- [ ] Task 7: Regenerate API client
  - [ ] 7.1 Run `pnpm generate:api` in frontend workspace
  - [ ] 7.2 Verify import types are generated

## Dev Notes

### Architecture Compliance

- **ARCH-13**: RBAC - Only owner can import members (sensitive operation)
- **ARCH-24**: All API/DB fields use `snake_case`
- **ARCH-27**: UUIDs for all primary keys
- **ARCH-28**: Standard error response format
- **ARCH-29**: Consumer profiles are platform-owned (shared identity)
- **FR30**: Gym owners can import existing members from spreadsheet

### Import Flow

```
1. Upload CSV/XLSX → returns columns + preview
2. Map columns → validate required fields mapped
3. Preview import → validate all rows, flag duplicates
4. Confirm import → create records, return results
```

### GymMembership Model

```python
class MembershipStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class GymMembership(GymScopedSoftDeleteModel, table=True):
    """Links consumers to gyms as members."""
    __tablename__ = "gym_memberships"

    consumer_id: UUID = Field(foreign_key="consumers.id", index=True)
    status: MembershipStatus = Field(default=MembershipStatus.PENDING)
    imported_at: datetime | None = Field(default=None)
    membership_tier: str | None = Field(default=None, max_length=100)

    __table_args__ = (
        UniqueConstraint("gym_id", "consumer_id", name="uq_gym_membership"),
    )
```

### Upload Response Schema

```python
class ImportUploadResponse(SQLModel):
    import_id: str  # Temporary ID for this import session
    file_name: str
    row_count: int
    columns: list[str]
    preview_rows: list[dict[str, str]]  # First 5 rows
```

### Mapping Request Schema

```python
class ImportMappingRequest(SQLModel):
    import_id: str
    mapping: dict[str, str]  # {file_column: field_name}
    # Required fields: email, first_name, last_name
    # Optional: phone, membership_tier
```

### Preview Response Schema

```python
class ImportPreviewRow(SQLModel):
    row_number: int
    data: dict[str, str]
    is_valid: bool
    errors: list[str]  # ["Invalid email format", "Missing first name"]
    is_duplicate: bool
    duplicate_type: str | None  # "file" or "database"

class ImportPreviewResponse(SQLModel):
    import_id: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    rows: list[ImportPreviewRow]
```

### Import Results Schema

```python
class ImportResultsResponse(SQLModel):
    import_id: str
    consumers_created: int
    memberships_created: int
    rows_skipped: int
    errors: list[dict]  # [{row: 5, error: "Duplicate email"}]
```

### File Handling

```python
# Use python-multipart for file uploads
# Use openpyxl for XLSX, csv module for CSV

import csv
from openpyxl import load_workbook

def parse_csv(file) -> tuple[list[str], list[dict]]:
    reader = csv.DictReader(file)
    columns = reader.fieldnames
    rows = list(reader)
    return columns, rows

def parse_xlsx(file) -> tuple[list[str], list[dict]]:
    wb = load_workbook(file)
    ws = wb.active
    columns = [cell.value for cell in ws[1]]
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        rows.append(dict(zip(columns, row)))
    return columns, rows
```

### Temporary Storage

Store uploaded files in `/tmp/imports/{import_id}/` with 1-hour TTL.
Use Redis or simple file cleanup for production.

### Dependencies

- Story 2.1: Gym Registration (COMPLETE) - Consumer model exists
- Integration point for Epic 4 (Membership Plans)

---

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

