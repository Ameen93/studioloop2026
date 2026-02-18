# 6-2-book-class-with-pay-per-class

## Status
in-progress

## Implementation Notes
Implemented pay-per-class booking endpoint.
- POST /api/v1/gyms/consumer/bookings/pay_per_class
- Persists booking_type=pay_per_class, price_paid_cents, source
- Increments spots_booked

## Validation
- Python compile check passed
- Automated pytest blocked by pre-existing Alembic revision mismatch in environment (`b5e1c4f9a222` missing)

## Claude Review
- Skipped: Claude Code tool not available in this execution environment
