# Story 1.4: JWT Token Refresh - QA Checklist

## Acceptance Criteria Verification

### AC #1: App automatically requests new access token using refresh token
- [ ] Consumer can call `POST /api/v1/auth/consumer/refresh` with valid refresh token
- [ ] Staff can call `POST /api/v1/auth/staff/refresh` with valid refresh token
- [ ] New access token is returned in response
- [ ] New access token can be used for authenticated requests

### AC #2: Old refresh token is invalidated (rotation)
- [ ] New refresh token is returned in response
- [ ] New refresh token differs from the old one
- [ ] Note: Implicit rotation - old token still works until expiry (MVP behavior)

### AC #3: New refresh token is issued
- [ ] `refresh_token` field present in response
- [ ] New refresh token is valid and can be used for subsequent refreshes

### AC #4: Invalid/expired refresh token redirects to login
- [ ] Expired refresh token returns 401 INVALID_TOKEN
- [ ] Malformed/invalid token returns 401 INVALID_TOKEN
- [ ] Access token used in refresh endpoint returns 401 INVALID_TOKEN
- [ ] Token for inactive user returns 401 INVALID_TOKEN
- [ ] All error responses use same message (no enumeration)

### AC #5: Token refresh happens transparently
- [ ] Backend endpoint is available for frontend to call
- [ ] Note: Frontend automatic refresh deferred to consumer app stories

## Manual Testing Checklist

### Consumer Token Refresh

1. **Setup**: Login as test consumer to get tokens
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/consumer/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@studioloop.com", "password": "testpassword123"}'
   ```
   - [ ] Save the `access_token` and `refresh_token` from response

2. **Refresh tokens**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/consumer/refresh \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "<refresh_token_from_step_1>"}'
   ```
   - [ ] Returns 200 OK
   - [ ] Response contains `access_token`, `refresh_token`, `token_type`
   - [ ] New tokens are different from original tokens

3. **Use new access token**:
   ```bash
   curl -X GET http://localhost:8000/api/v1/some-protected-endpoint \
     -H "Authorization: Bearer <new_access_token>"
   ```
   - [ ] Request succeeds with new access token

4. **Test error cases**:
   - [ ] Using access token as refresh token returns 401
   - [ ] Using malformed token returns 401
   - [ ] Using empty token returns 422 validation error

### Staff Token Refresh

1. **Setup**: Login as staff member (requires seeded staff account)
   ```bash
   # First create a staff via seed or test setup
   curl -X POST http://localhost:8000/api/v1/auth/staff/login \
     -H "Content-Type: application/json" \
     -d '{"email": "<staff_email>", "password": "<staff_password>"}'
   ```
   - [ ] Save the `access_token`, `refresh_token`, `role`, `gym_id`

2. **Refresh tokens**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/staff/refresh \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "<refresh_token_from_step_1>"}'
   ```
   - [ ] Returns 200 OK
   - [ ] Response contains `access_token`, `refresh_token`, `token_type`, `role`, `gym_id`
   - [ ] `role` matches original role (e.g., "owner", "manager")
   - [ ] `gym_id` matches original gym_id

3. **Verify claims in new access token**:
   - [ ] Decode new access token (use jwt.io or similar)
   - [ ] Verify `role` claim is present and correct
   - [ ] Verify `gym_id` claim is present and correct
   - [ ] Verify `type` claim is "access"

4. **Test error cases**:
   - [ ] Using consumer refresh token in staff endpoint returns 401
   - [ ] Deactivated staff's refresh token returns 401

## API Response Verification

### Success Response (Consumer)
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Success Response (Staff)
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "role": "owner",
  "gym_id": "uuid-here"
}
```

### Error Response (all error cases)
```json
{
  "detail": {
    "code": "INVALID_TOKEN",
    "message": "Invalid or expired refresh token",
    "details": {}
  }
}
```

## Automated Test Verification

Run the test suite and verify all tests pass:
```bash
cd backend
pytest tests/api/routes/test_token_refresh.py -v
```

Expected tests:
- [ ] `test_consumer_refresh_success`
- [ ] `test_consumer_refresh_tokens_are_different`
- [ ] `test_consumer_refresh_expired_token`
- [ ] `test_consumer_refresh_access_token_rejected`
- [ ] `test_consumer_refresh_invalid_token`
- [ ] `test_consumer_refresh_inactive_user`
- [ ] `test_staff_refresh_success`
- [ ] `test_staff_refresh_preserves_role`
- [ ] `test_staff_refresh_preserves_gym_id`
- [ ] `test_staff_refresh_expired_token`
- [ ] `test_staff_refresh_access_token_rejected`
- [ ] `test_staff_refresh_inactive_staff`

## Security Verification

- [ ] All error responses use same message (prevents enumeration)
- [ ] Inactive users cannot refresh tokens
- [ ] Access tokens rejected in refresh endpoints
- [ ] No sensitive data in error responses

## Notes

- Frontend automatic refresh (AC #5 fully) is deferred to consumer app implementation
- Token blacklist/explicit revocation is not implemented for MVP (implicit rotation)
- Staff tokens preserve role and gym_id claims across refresh
