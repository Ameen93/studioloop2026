# 6-12-booking-source-tracking

## Status
in-progress

## Implementation Notes
Implemented booking.source persistence and API input enums.
- direct/marketplace persisted on booking
- Included in test coverage for pay-per-class path

## Validation
- Python compile check passed
- Automated pytest blocked by pre-existing Alembic revision mismatch in environment (`b5e1c4f9a222` missing)

## Claude Review
- Skipped: Claude Code tool not available in this execution environment
