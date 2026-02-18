from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlmodel import select

from app.api.deps import CurrentConsumer, SessionDep
from app.models import ClassSession, ClassSessionStatus, Gym, Space

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


class MarketplaceClassItem(BaseModel):
    session_id: UUID
    gym_id: UUID
    gym_name: str
    title: str
    start_time: datetime
    end_time: datetime
    capacity: int
    spots_booked: int
    price_cents: int
    city: str | None
    province: str | None
    space_name: str | None


@router.get("/classes", response_model=list[MarketplaceClassItem])
def browse_marketplace_classes(
    _current_consumer: CurrentConsumer,
    session: SessionDep,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[MarketplaceClassItem]:
    now = datetime.now(timezone.utc)

    rows = session.exec(
        select(ClassSession, Gym, Space)
        .join(Gym, Gym.id == ClassSession.gym_id)
        .join(Space, Space.id == ClassSession.space_id)
        .where(
            ClassSession.is_active.is_(True),
            Gym.is_active.is_(True),
            Gym.is_marketplace_enabled.is_(True),
            Space.is_active.is_(True),
            ClassSession.status == ClassSessionStatus.SCHEDULED,
            ClassSession.start_time >= now,
        )
        .order_by(ClassSession.start_time)
        .limit(limit)
    ).all()

    return [
        MarketplaceClassItem(
            session_id=class_session.id,
            gym_id=gym.id,
            gym_name=gym.name,
            title=class_session.title,
            start_time=class_session.start_time,
            end_time=class_session.end_time,
            capacity=class_session.capacity,
            spots_booked=class_session.spots_booked,
            price_cents=class_session.price_cents,
            city=gym.city,
            province=gym.province,
            space_name=space.name,
        )
        for class_session, gym, space in rows
    ]
