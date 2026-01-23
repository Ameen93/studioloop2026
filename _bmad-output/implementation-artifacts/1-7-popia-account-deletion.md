# Story 1.7: POPIA Account Deletion

Status: ready-for-dev

## Story

As a **consumer**,
I want to delete my account and all associated data,
So that I can exercise my POPIA right to erasure.

## Acceptance Criteria

1. **Given** I am logged in and request account deletion
   **When** I confirm the deletion request
   **Then** my account is marked for deletion

2. **And** I receive confirmation email

3. **And** all my personal data is deleted within 30 days per NFR13

4. **And** my bookings are anonymized (not deleted for gym records)

5. **And** my memberships are cancelled

6. **And** I am logged out and cannot login again

## Tasks / Subtasks

- [ ] Task 1: Create account deletion request endpoint (AC: #1, #6)
  - [ ] 1.1 Create `DELETE /auth/consumer/me` endpoint in `consumers.py`
  - [ ] 1.2 Require authenticated consumer via `CurrentConsumer` dependency
  - [ ] 1.3 Require password confirmation in request body for security
  - [ ] 1.4 Call `consumer.soft_delete()` to mark account as deleted
  - [ ] 1.5 Increment `token_version` to invalidate ALL existing tokens
  - [ ] 1.6 Set `deletion_requested_at` timestamp for 30-day countdown
  - [ ] 1.7 Return success response with logout instructions

- [ ] Task 2: Add deletion tracking fields to Consumer model (AC: #3)
  - [ ] 2.1 Add `deletion_requested_at: datetime | None` field to Consumer model
  - [ ] 2.2 Create Alembic migration for new field
  - [ ] 2.3 Field tracks when 30-day deletion window started

- [ ] Task 3: Send deletion confirmation email (AC: #2)
  - [ ] 3.1 Create email template `account_deletion_confirmation.html`
  - [ ] 3.2 Add `generate_account_deletion_email()` function in `utils.py`
  - [ ] 3.3 Send email after successful deletion request
  - [ ] 3.4 Include: confirmation message, 30-day timeline, contact info for reversal

- [ ] Task 4: Create account deletion request schema
  - [ ] 4.1 Create `AccountDeletionRequest` schema with `password: str` field
  - [ ] 4.2 Add to `models/__init__.py` exports

- [ ] Task 5: Prevent deleted account login (AC: #6)
  - [ ] 5.1 Verify `is_active=False` check in consumer login already rejects deleted accounts
  - [ ] 5.2 Verify `CurrentConsumer` dependency rejects inactive consumers
  - [ ] 5.3 Ensure error message is generic (no enumeration: "Invalid credentials")

- [ ] Task 6: Add backend tests for account deletion
  - [ ] 6.1 Test DELETE /me with correct password succeeds (200)
  - [ ] 6.2 Test DELETE /me sets `is_active=False` and `deleted_at`
  - [ ] 6.3 Test DELETE /me sets `deletion_requested_at` timestamp
  - [ ] 6.4 Test DELETE /me increments `token_version` (invalidates tokens)
  - [ ] 6.5 Test DELETE /me with wrong password fails (401 INVALID_CREDENTIALS)
  - [ ] 6.6 Test DELETE /me without authentication fails (401)
  - [ ] 6.7 Test deleted consumer cannot login (401 INVALID_CREDENTIALS)
  - [ ] 6.8 Test deleted consumer's existing tokens are invalidated (401 on /me)
  - [ ] 6.9 Test email is sent on successful deletion (mock)

- [ ] Task 7: Document DEFERRED items for future implementation
  - [ ] 7.1 Document: Booking anonymization (requires Booking model - Epic 6)
  - [ ] 7.2 Document: Membership cancellation (requires Membership model - Epic 4)
  - [ ] 7.3 Document: Background job for 30-day data purge (requires job scheduler)
  - [ ] 7.4 Document: Admin endpoint to view pending deletions

## Dev Notes

### Architecture Compliance

- **ARCH-10**: Custom JWT (FastAPI native) for authentication
- **ARCH-11**: Argon2 password hashing for deletion confirmation
- **ARCH-12**: Token version increment to invalidate all sessions
- **ARCH-28**: Standard error response format with code, message, details
- **NFR13**: POPIA compliance - data export/deletion within 30 days
- **NFR35**: Data residency in SA-based hosting
- **NFR37**: Consent tracking - record deletion request with timestamp

### Existing Code to Reuse

**SoftDeleteMixin (`backend/app/models/base.py:62-85`):**
```python
class SoftDeleteMixin:
    """Mixin providing soft-delete capability."""

    is_active: bool = Field(
        default=True,
        nullable=False,
        index=True,
        description="Whether this record is active (soft-delete flag)",
    )
    deleted_at: datetime | None = Field(
        default=None,
        nullable=True,
        description="Timestamp when record was soft-deleted (UTC)",
    )

    def soft_delete(self) -> None:
        """Mark record as soft-deleted."""
        self.is_active = False
        self.deleted_at = datetime.now(timezone.utc)
```

**Consumer model already uses SoftDeleteMixin (`backend/app/models/consumer.py:56`):**
```python
class Consumer(SoftDeleteMixin, BaseModel, ConsumerBase, table=True):
    """Consumer model - platform-scoped user identity.

    POPIA Compliance:
    - Consumers can request account deletion
    - Soft-delete preserves audit trail
    - Personal data can be anonymized
    """
```

**Token version for session invalidation (`backend/app/models/consumer.py:114-118`):**
```python
# Token rotation (ARCH-12)
token_version: int = Field(
    default=1,
    description="Incremented on token refresh to invalidate old refresh tokens",
)
```

**CurrentConsumer dependency (`backend/app/api/deps.py`):**
- Already validates `is_active` - deleted accounts cannot authenticate
- Already validates token type is "access"

**Password verification (`backend/app/core/security.py`):**
```python
from app.core.security import verify_password
```

### Implementation Patterns

**Deletion endpoint pattern:**
```python
class AccountDeletionRequest(SQLModel):
    """Schema for account deletion - requires password confirmation."""
    password: str = Field(min_length=8, description="Current password for confirmation")


@router.delete("/me", response_model=Message)
def delete_consumer_account(
    session: SessionDep,
    current_consumer: CurrentConsumer,
    deletion_request: AccountDeletionRequest,
) -> Message:
    """Delete consumer account (POPIA right to erasure).

    Requires password confirmation for security.
    Marks account for deletion, invalidates all sessions,
    and schedules data cleanup within 30 days.

    Args:
        session: Database session
        current_consumer: Authenticated consumer from JWT
        deletion_request: Password confirmation

    Returns:
        Message confirming deletion scheduled

    Raises:
        HTTPException: 401 INVALID_CREDENTIALS if password wrong
    """
    # Verify password
    if not verify_password(deletion_request.password, current_consumer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid password",
                "details": {},
            },
        )

    # Mark account for deletion using SoftDeleteMixin
    current_consumer.soft_delete()

    # Set deletion requested timestamp for 30-day countdown
    current_consumer.deletion_requested_at = datetime.now(timezone.utc)

    # CRITICAL: Invalidate ALL tokens by incrementing version
    current_consumer.token_version += 1

    session.add(current_consumer)
    session.commit()

    # Send confirmation email
    if settings.emails_enabled:
        email_data = generate_account_deletion_email(
            email_to=current_consumer.email,
            first_name=current_consumer.first_name,
        )
        send_email(
            email_to=current_consumer.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    return Message(message="Account deletion scheduled. Your data will be removed within 30 days.")
```

**Email template function:**
```python
def generate_account_deletion_email(
    email_to: str,
    first_name: str,
) -> EmailData:
    """Generate account deletion confirmation email."""
    subject = f"{settings.PROJECT_NAME} - Account Deletion Confirmation"
    html_content = f"""
    <html>
    <body>
        <p>Hi {first_name},</p>
        <p>We've received your request to delete your StudioLoop account.</p>
        <p>Your account has been deactivated immediately, and all your personal data
        will be permanently deleted within 30 days as required by POPIA.</p>
        <p>If you did not request this deletion or wish to cancel, please contact
        us immediately at support@studioloop.co.za.</p>
        <p>Thank you for using StudioLoop.</p>
    </body>
    </html>
    """
    return EmailData(subject=subject, html_content=html_content)
```

### Error Response Format

All errors use standard format (ARCH-28):
```json
{
  "detail": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid password",
    "details": {}
  }
}
```

### Testing Patterns

```python
class TestAccountDeletion:
    """Tests for consumer account deletion endpoint."""

    def test_delete_account_success(self, client, db: Session):
        """Test DELETE /me with correct password."""
        consumer, token = create_consumer_with_token(db)

        response = client.delete(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"password": "testpassword123"},
        )

        assert response.status_code == 200
        assert "deletion scheduled" in response.json()["message"].lower()

        # Verify consumer is soft-deleted
        db.refresh(consumer)
        assert consumer.is_active is False
        assert consumer.deleted_at is not None
        assert consumer.deletion_requested_at is not None

    def test_delete_account_wrong_password(self, client, db: Session):
        """Test DELETE /me with wrong password fails."""
        consumer, token = create_consumer_with_token(db)

        response = client.delete(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"

    def test_deleted_consumer_cannot_login(self, client, db: Session):
        """Test deleted consumer cannot login."""
        # Create consumer, delete, then try to login
        email = random_email()
        password = "testpassword123"
        consumer = create_verified_consumer(db, email=email, password=password)

        # Delete the account
        consumer.soft_delete()
        consumer.token_version += 1
        db.commit()

        # Try to login
        response = client.post(
            f"{settings.API_V1_STR}/auth/consumer/login",
            json={"email": email, "password": password},
        )

        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"

    def test_deleted_consumer_tokens_invalidated(self, client, db: Session):
        """Test existing tokens are invalidated after deletion."""
        consumer, token = create_consumer_with_token(db)

        # Token works before deletion
        response = client.get(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        # Delete the account
        consumer.soft_delete()
        consumer.token_version += 1
        db.commit()

        # Same token should now fail
        response = client.get(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
```

### Previous Story Intelligence

From Story 1.6 (Profile Management):
- `CurrentConsumer` dependency pattern for authenticated endpoints
- `validate_sa_phone()` utility function pattern
- Partial update with `model_dump(exclude_unset=True)`
- Null validation for non-nullable fields

From Story 1.5 (Password Reset):
- Token version increment pattern for session invalidation
- Email sending pattern with `send_email()` and `EmailData`
- Error response format with code, message, details

From Story 1.2 (Consumer Login):
- `verify_password()` for password confirmation
- Login rejection for inactive accounts (`is_active=False`)

### What NOT to Do

- **DO NOT** hard delete consumer data immediately (soft-delete first, purge after 30 days)
- **DO NOT** reveal account existence in error messages (use generic "Invalid credentials")
- **DO NOT** implement booking anonymization in this story (requires Epic 6 Booking model)
- **DO NOT** implement membership cancellation in this story (requires Epic 4 Membership model)
- **DO NOT** implement background job for 30-day purge (requires job scheduler infrastructure)
- **DO NOT** allow deletion without password confirmation (security requirement)
- **DO NOT** send email if `settings.emails_enabled` is False

### DEFERRED for Future Epics

**Epic 4 - Membership Cancellation:**
When Membership model exists, update deletion to:
- Cancel all active memberships
- Trigger refund workflows if applicable

**Epic 6 - Booking Anonymization:**
When Booking model exists, update deletion to:
- Replace consumer_id with "DELETED_USER" placeholder
- Remove personal details from booking notes
- Preserve booking record for gym analytics

**Epic Infrastructure - 30-Day Purge Job:**
Background job that:
- Finds consumers with `deletion_requested_at` > 30 days ago
- Permanently deletes/anonymizes all personal data
- Removes from database or anonymizes

### Project Structure Notes

Files to create/modify:
```
backend/
├── app/
│   ├── api/routes/
│   │   └── consumers.py          # UPDATE: Add DELETE /me endpoint
│   ├── models/
│   │   ├── consumer.py           # UPDATE: Add deletion_requested_at field
│   │   └── __init__.py           # UPDATE: Export AccountDeletionRequest
│   └── utils.py                  # UPDATE: Add generate_account_deletion_email()
├── alembic/versions/
│   └── xxxx_add_deletion_requested_at.py  # NEW: Migration
└── tests/api/routes/
    └── test_account_deletion.py  # NEW: Deletion tests
```

### Dependencies on Previous Stories

- Story 1-1: Consumer registration (COMPLETE) - Consumer model, SoftDeleteMixin
- Story 1-2: Consumer login (REVIEW) - Login rejection for inactive accounts
- Story 1-5: Password reset (REVIEW) - Email sending pattern, token invalidation
- Story 1-6: Profile management (REVIEW) - CurrentConsumer dependency

### Migration Notes

**Adding `deletion_requested_at` column:**
```python
# alembic/versions/xxxx_add_deletion_requested_at.py
def upgrade():
    op.add_column(
        'consumers',
        sa.Column('deletion_requested_at', sa.DateTime(timezone=True), nullable=True)
    )

def downgrade():
    op.drop_column('consumers', 'deletion_requested_at')
```

### References

- [Source: epics.md#Story 1.7 - POPIA Account Deletion]
- [Source: architecture.md - NFR13 POPIA deletion within 30 days]
- [Source: architecture.md - ARCH-12 Token management]
- [Source: architecture.md - ARCH-28 Error format]
- [Source: backend/app/models/base.py - SoftDeleteMixin]
- [Source: backend/app/models/consumer.py - Consumer model with soft-delete]

---

## QA Checklist

### Account Deletion Tests

- [ ] **DELETE /auth/consumer/me**
  - [ ] Returns 200 with success message when password is correct
  - [ ] Sets `is_active=False` on consumer record
  - [ ] Sets `deleted_at` timestamp on consumer record
  - [ ] Sets `deletion_requested_at` timestamp for 30-day tracking
  - [ ] Increments `token_version` to invalidate sessions
  - [ ] Returns 401 INVALID_CREDENTIALS when password is wrong
  - [ ] Returns 401 when no authentication token provided
  - [ ] Returns 401 when token is invalid/expired
  - [ ] Sends confirmation email (when emails_enabled=True)

### Post-Deletion Behavior Tests

- [ ] **Deleted consumer cannot login**
  - [ ] Login attempt returns 401 INVALID_CREDENTIALS
  - [ ] Error message does NOT reveal account was deleted (privacy)

- [ ] **Existing tokens are invalidated**
  - [ ] Previously valid access token returns 401 after deletion
  - [ ] Previously valid refresh token returns 401 after deletion

- [ ] **Profile endpoints reject deleted accounts**
  - [ ] GET /auth/consumer/me returns 401 after deletion
  - [ ] PATCH /auth/consumer/me returns 401 after deletion

### Security Tests

- [ ] Password confirmation required (cannot delete without password)
- [ ] Generic error messages (no account enumeration)
- [ ] Token version increment prevents token reuse

### Email Tests

- [ ] Confirmation email sent to consumer's email address
- [ ] Email includes 30-day timeline information
- [ ] Email includes contact info for reversal request
- [ ] Email NOT sent when `emails_enabled=False`

---

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Completion Notes

(To be filled by dev agent after implementation)

### File List

**Modified:**
- `backend/app/api/routes/consumers.py` - Add DELETE /me endpoint
- `backend/app/models/consumer.py` - Add deletion_requested_at field
- `backend/app/models/__init__.py` - Export AccountDeletionRequest
- `backend/app/utils.py` - Add generate_account_deletion_email()

**Created:**
- `backend/alembic/versions/xxxx_add_deletion_requested_at.py` - Migration
- `backend/tests/api/routes/test_account_deletion.py` - Tests
