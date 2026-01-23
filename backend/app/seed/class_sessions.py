"""Seed data for ClassSession entities.

DEFERRED: ClassSession model will be created in Epic 5 (Class Scheduling System).

This module is a placeholder that documents the planned class session
seed data structure for when the model becomes available.

Planned Class Sessions:
- Generate sessions for the next 14 days
- Each gym gets sessions based on their class templates
- Mix of morning (6am-9am), lunch (12pm-1pm), and evening (5pm-8pm) times
- Some sessions nearly full, some with availability, some waitlisted
- Weekend schedules differ from weekday schedules
"""

from sqlmodel import Session

# Documented for future implementation
PLANNED_SESSION_PATTERNS = {
    "weekday": {
        "morning": ["06:00", "07:00", "08:00"],
        "lunch": ["12:00", "12:30"],
        "evening": ["17:00", "18:00", "19:00", "20:00"],
    },
    "weekend": {
        "morning": ["08:00", "09:00", "10:00", "11:00"],
        "afternoon": ["14:00", "15:00", "16:00"],
    },
}


def seed_class_sessions(_session: Session) -> int:
    """Seed class sessions for the next 14 days.

    DEFERRED: Returns 0 until ClassSession model is created in Epic 5.

    Planned implementation:
    - Generate sessions for each gym's templates
    - Create realistic schedules (different weekday/weekend patterns)
    - Vary capacity utilization (some full, some available)
    - Include past sessions (yesterday) for history testing
    - Include future sessions (next 14 days) for booking testing

    Args:
        session: SQLModel database session

    Returns:
        Number of sessions created (currently 0)
    """
    # TODO: Implement when ClassSession model is created in Epic 5
    # See Epic 5: Class Scheduling System for model definition

    return 0
