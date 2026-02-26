# User Testing - Story 2.1: Gym Registration and Owner Account

## Status
Ready for user testing

## Scope
- Register a gym with owner credentials
- Confirm gym + owner staff creation
- Validate duplicate slug/email guardrails
- Validate SA phone format enforcement

## Manual Test Checklist
- [ ] Submit valid payload to `POST /api/v1/gyms/register`
- [ ] Verify response includes `gym_id`, `owner_staff_id`
- [ ] Verify owner has role `owner` and `is_email_verified=false`
- [ ] Submit duplicate `gym_slug` and confirm `GYM_SLUG_ALREADY_EXISTS`
- [ ] Submit duplicate `owner_email` and confirm `OWNER_EMAIL_ALREADY_EXISTS`
- [ ] Submit invalid phone and confirm `INVALID_PHONE_FORMAT`
