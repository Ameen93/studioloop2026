"""Repair legacy local alembic version pointers.

Some local dev databases were stamped with a removed revision id (`b5e1c4f9a222`).
This script remaps that orphaned revision to the nearest surviving revision so
`alembic upgrade head` can proceed.
"""

from __future__ import annotations

from sqlalchemy import create_engine, text

from app.core.config import settings

LEGACY_REVISION = "b5e1c4f9a222"
REMAPPED_REVISION = "a7c9d2e4b123"


def main() -> None:
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    with engine.begin() as conn:
        current = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()
        if current != LEGACY_REVISION:
            print(f"No repair needed. Current revision: {current}")
            return

        conn.execute(
            text("UPDATE alembic_version SET version_num = :target"),
            {"target": REMAPPED_REVISION},
        )
        print(
            "Updated alembic_version from "
            f"{LEGACY_REVISION} -> {REMAPPED_REVISION}. "
            "Run `uv run alembic upgrade head` next."
        )


if __name__ == "__main__":
    main()
