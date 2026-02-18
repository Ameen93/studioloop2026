from datetime import date, datetime, time, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
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
    class_type: str | None = Query(default=None, min_length=1, max_length=80),
    city: str | None = Query(default=None, min_length=1, max_length=100),
    province: str | None = Query(default=None, min_length=1, max_length=100),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    start_time_from: time | None = Query(default=None),
    start_time_to: time | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[MarketplaceClassItem]:
    now = datetime.now(timezone.utc)

    query = (
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
    )
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be on or before end_date")
    if start_time_from and start_time_to and start_time_from > start_time_to:
        raise HTTPException(status_code=400, detail="start_time_from must be on or before start_time_to")

    if class_type:
        class_type_value = class_type.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.where(ClassSession.title.ilike(f"%{class_type_value}%", escape="\\"))
    if city:
        city_value = city.strip().lower()
        query = query.where(func.lower(Gym.city) == city_value)
    if province:
        province_value = province.strip().lower()
        query = query.where(func.lower(Gym.province) == province_value)
    if start_date:
        query = query.where(ClassSession.start_time >= datetime.combine(start_date, time.min, tzinfo=timezone.utc))
    if end_date:
        query = query.where(ClassSession.start_time <= datetime.combine(end_date, time.max, tzinfo=timezone.utc))
    rows = session.exec(query.order_by(ClassSession.start_time)).all()

    if start_time_from or start_time_to:
        filtered_rows: list[tuple[ClassSession, Gym, Space]] = []
        for class_session, gym, space in rows:
            session_time = class_session.start_time.time()
            if start_time_from and session_time < start_time_from:
                continue
            if start_time_to and session_time > start_time_to:
                continue
            filtered_rows.append((class_session, gym, space))
        rows = filtered_rows

    rows = rows[:limit]

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
