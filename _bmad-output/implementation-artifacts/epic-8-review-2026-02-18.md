# Epic 8 Review — 2026-02-18

## Scope Reviewed
Stories 8-1 through 8-9 (Payments & Billing).

## Review Method
Claude CLI unavailable in this runtime. Performed equivalent structured engineering review covering:
- architecture/compliance with epic acceptance criteria
- tenant isolation and authz boundaries
- idempotency/error handling for webhooks
- retry lifecycle correctness
- output privacy and POPIA-safe response surfaces
- test coverage for critical happy-path + failure-path flows

## Findings and Fixes Applied
1. **Reserved ORM attribute conflict** (`metadata`) in `Payment` model.
   - **Fix:** renamed model attribute to `extra_data` with DB column name still `metadata`.
2. **Route ambiguity** for payout report path versus payment detail path.
   - **Fix:** moved payout report to `/payments/gyms/{gym_id}/reports/marketplace-payout`.
3. **Type-check issues** in SQL expression usage under strict mypy.
   - **Fix:** replaced fragile expression patterns with explicit Python-side filtering/sorting where needed.
4. **Membership failure assertion flake in test context cache.**
   - **Fix:** refreshed ORM instance in test before assertion.

## Validation Evidence
- `uv run ruff check app/api/routes/payments.py app/models/payment.py app/services/payments/providers.py tests/api/routes/test_payments.py`
- `uv run mypy app/api/routes/payments.py app/models/payment.py app/services/payments/providers.py`
- `uv run pytest tests/api/routes/test_payments.py -q`
- `uv run pytest tests/api/routes/test_staff_memberships.py tests/api/routes/test_marketplace.py tests/api/routes/test_payments.py -q`

All commands passed.

## Remaining Manual/Secrets-Gated Items
- Real Ozow/PayFast credentials + production webhook signing secrets (secrets-gated).
- Production email/push provider wiring for payment failure + receipt mail delivery (manual infra/config step).
