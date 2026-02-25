"""Seed data for ClassSession entities used as recurring templates.

Note: The project doesn't have a separate ClassTemplate model — class sessions
serve as individual scheduled classes. This module is kept for compatibility
with the orchestrator interface but the actual session generation happens
in class_sessions.py. This returns 0 since templates aren't a separate entity.
"""

from typing import TYPE_CHECKING

from sqlmodel import Session

if TYPE_CHECKING:
    from app.models import Gym


def seed_class_templates(_session: Session, _gyms: list["Gym"]) -> int:
    """No-op: class templates are not a separate model.

    Class sessions are created directly in seed_class_sessions.

    Returns:
        0 (no separate template model)
    """
    return 0
