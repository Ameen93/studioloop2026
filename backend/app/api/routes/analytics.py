from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import UTC, date, datetime, time, timedelta
from io import StringIO
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import col, select

from app.api.deps import CurrentConsumer, RequireOwnerOrManager, SessionDep, StaffGymDep
from app.models.booking import Booking, BookingStatus
from app.models.check_in_record import CheckInRecord
from app.models.class_session import ClassSession
from app.models.consumer import Consumer
from app.models.gym_membership import GymMembership, GymMembershipStatus
from app.models.payment import Payment, PaymentStatus, PaymentType
from app.models.staff import Staff, StaffRole

router = APIRouter(prefix="/analytics", tags=["analytics"])


class RevenueSourceBreakdown(BaseModel):
    memberships_cents: int
    classes_cents: int
    marketplace_cents: int


class RevenueReportResponse(BaseModel):
    period: str
    start_date: date
    end_date: date
    total_revenue_cents: int
    source_breakdown: RevenueSourceBreakdown
    previous_period_total_cents: int
    growth_percent: float
    daily_totals: list[dict[str, int | str]]


class AttendanceReportResponse(BaseModel):
    period: str
    start_date: date
    end_date: date
    total_check_ins: int
    by_day_of_week: list[dict[str, int | str]]
    by_hour_of_day: list[dict[str, int]]
    peak_hour: int | None
    average_daily_attendance: float
    average_weekly_attendance: float


class MembershipHealthResponse(BaseModel):
    period: str
    start_date: date
    end_date: date
    total_active_members: int
    new_this_period: int
    cancelled_this_period: int
    churn_rate_percent: float
    retention_rate_percent: float
    tier_breakdown: list[dict[str, int | str]]
    expiring_soon_member_count: int


class ClassPerformanceItem(BaseModel):
    session_id: UUID
    class_name: str
    instructor_staff_id: UUID | None
    fill_rate_percent: float
    attendance_rate_percent: float
    no_show_rate_percent: float
    bookings: int
    capacity: int


class ClassPerformanceResponse(BaseModel):
    period: str
    start_date: date
    end_date: date
    items: list[ClassPerformanceItem]
    popular_classes: list[str]
    underperforming_sessions: list[UUID]


class StaffPerformanceItem(BaseModel):
    staff_id: UUID
    full_name: str
    role: str
    classes_taught: int
    avg_fill_rate_percent: float
    total_hours_worked: float
    estimated_earnings_cents: int | None


class ConsumerClassHistoryItem(BaseModel):
    session_id: UUID
    class_name: str
    gym_id: UUID
    instructor_name: str | None
    attended_at: datetime


class ConsumerClassHistoryResponse(BaseModel):
    items: list[ConsumerClassHistoryItem]
    total_attended_this_month: int
    total_attended_this_year: int


class ConsumerStatsResponse(BaseModel):
    total_classes_all_time: int
    total_classes_this_month: int
    favorite_class_type: str | None
    most_visited_gym_id: UUID | None
    current_streak_weeks: int
    average_classes_per_week: float


class AtRiskMemberItem(BaseModel):
    consumer_id: UUID
    full_name: str
    last_check_in_at: datetime | None
    days_since_last_check_in: int | None
    recent_4_weeks_check_ins: int
    previous_4_weeks_check_ins: int


class AtRiskRunResponse(BaseModel):
    gym_id: UUID
    evaluated_members: int
    flagged_members: int


class GymOwnerDashboardResponse(BaseModel):
    gym_id: UUID
    action_items: dict[str, int]
    today_summary: dict[str, int]
    quick_metrics: dict[str, float | int]


def _period_bounds(
    period: str, start_date: date | None, end_date: date | None
) -> tuple[datetime, datetime]:
    today = datetime.now(UTC).date()
    if period == "daily":
        start = datetime.combine(today, time.min, tzinfo=UTC)
        end = datetime.combine(today, time.max, tzinfo=UTC)
    elif period == "weekly":
        week_start = today - timedelta(days=today.weekday())
        start = datetime.combine(week_start, time.min, tzinfo=UTC)
        end = datetime.combine(today, time.max, tzinfo=UTC)
    elif period == "monthly":
        month_start = today.replace(day=1)
        start = datetime.combine(month_start, time.min, tzinfo=UTC)
        end = datetime.combine(today, time.max, tzinfo=UTC)
    elif period == "custom":
        if not start_date or not end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date and end_date required for custom period",
            )
        start = datetime.combine(start_date, time.min, tzinfo=UTC)
        end = datetime.combine(end_date, time.max, tzinfo=UTC)
    else:
        raise HTTPException(status_code=400, detail="invalid period")
    if end < start:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")
    return start, end


def _percent(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


@router.get("/gyms/{gym_id}/revenue", response_model=RevenueReportResponse)
def revenue_report(
    gym_id: UUID,
    session: SessionDep,
    _staff: StaffGymDep,
    _role: None = RequireOwnerOrManager,
    period: str = Query(default="monthly"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    export: str | None = Query(default=None),
) -> RevenueReportResponse | Response:
    start, end = _period_bounds(period, start_date, end_date)
    duration = end - start
    prev_start = start - duration - timedelta(seconds=1)
    prev_end = start - timedelta(seconds=1)

    payments = session.exec(
        select(Payment).where(
            Payment.gym_id == gym_id,
            Payment.status == PaymentStatus.COMPLETED,
            col(Payment.completed_at).is_not(None),
            col(Payment.completed_at) >= start,
            col(Payment.completed_at) <= end,
        )
    ).all()

    prev_total: int = int(
        session.exec(
            select(func.coalesce(func.sum(Payment.amount_cents), 0)).where(
                Payment.gym_id == gym_id,
                Payment.status == PaymentStatus.COMPLETED,
                col(Payment.completed_at).is_not(None),
                col(Payment.completed_at) >= prev_start,
                col(Payment.completed_at) <= prev_end,
            )
        ).one()
        or 0
    )

    memberships = sum(
        p.amount_cents for p in payments if p.payment_type == PaymentType.MEMBERSHIP
    )
    classes = sum(
        p.amount_cents for p in payments if p.payment_type == PaymentType.CLASS_BOOKING
    )
    marketplace = sum(
        p.amount_cents
        for p in payments
        if p.payment_type == PaymentType.MARKETPLACE_SUBSCRIPTION
    )
    total = memberships + classes + marketplace

    daily: dict[str, int] = defaultdict(int)
    for p in payments:
        if p.completed_at:
            daily[p.completed_at.date().isoformat()] += p.amount_cents

    if export == "csv":
        sio = StringIO()
        writer = csv.writer(sio)
        writer.writerow(["date", "revenue_cents"])
        for d, v in sorted(daily.items()):
            writer.writerow([d, v])
        return Response(content=sio.getvalue(), media_type="text/csv")

    growth = (
        _percent(total - prev_total, prev_total)
        if prev_total > 0
        else (100.0 if total > 0 else 0.0)
    )
    return RevenueReportResponse(
        period=period,
        start_date=start.date(),
        end_date=end.date(),
        total_revenue_cents=total,
        source_breakdown=RevenueSourceBreakdown(
            memberships_cents=memberships,
            classes_cents=classes,
            marketplace_cents=marketplace,
        ),
        previous_period_total_cents=prev_total,
        growth_percent=growth,
        daily_totals=[
            {"date": d, "revenue_cents": v} for d, v in sorted(daily.items())
        ],
    )


@router.get("/gyms/{gym_id}/attendance", response_model=AttendanceReportResponse)
def attendance_report(
    gym_id: UUID,
    session: SessionDep,
    _staff: StaffGymDep,
    _role: None = RequireOwnerOrManager,
    period: str = Query(default="monthly"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    membership_tier: str | None = Query(default=None),
) -> AttendanceReportResponse:
    start, end = _period_bounds(period, start_date, end_date)
    check_ins = session.exec(
        select(CheckInRecord).where(
            CheckInRecord.gym_id == gym_id,
            col(CheckInRecord.checked_in_at) >= start,
            col(CheckInRecord.checked_in_at) <= end,
        )
    ).all()

    if membership_tier:
        memberships = session.exec(
            select(GymMembership).where(
                GymMembership.gym_id == gym_id,
                GymMembership.membership_tier == membership_tier,
            )
        ).all()
        allowed = {m.consumer_id for m in memberships}
        check_ins = [c for c in check_ins if c.consumer_id in allowed]

    by_day = Counter(c.checked_in_at.strftime("%A") for c in check_ins)
    by_hour = Counter(c.checked_in_at.hour for c in check_ins)
    total = len(check_ins)
    days = max((end.date() - start.date()).days + 1, 1)
    weeks = max(days / 7, 1)

    peak_hour = max(by_hour, key=lambda hour: by_hour[hour]) if by_hour else None
    return AttendanceReportResponse(
        period=period,
        start_date=start.date(),
        end_date=end.date(),
        total_check_ins=total,
        by_day_of_week=[
            {"day": d, "check_ins": by_day[d]} for d in sorted(by_day.keys())
        ],
        by_hour_of_day=[
            {"hour": h, "check_ins": by_hour[h]} for h in sorted(by_hour.keys())
        ],
        peak_hour=peak_hour,
        average_daily_attendance=round(total / days, 2),
        average_weekly_attendance=round(total / weeks, 2),
    )


@router.get("/gyms/{gym_id}/membership-health", response_model=MembershipHealthResponse)
def membership_health_report(
    gym_id: UUID,
    session: SessionDep,
    _staff: StaffGymDep,
    _role: None = RequireOwnerOrManager,
    period: str = Query(default="monthly"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
) -> MembershipHealthResponse:
    start, end = _period_bounds(period, start_date, end_date)
    memberships = session.exec(
        select(GymMembership).where(GymMembership.gym_id == gym_id)
    ).all()

    active = [m for m in memberships if m.status == GymMembershipStatus.ACTIVE]
    new_members = [m for m in memberships if start <= m.started_at <= end]
    cancelled = [
        m
        for m in memberships
        if m.status == GymMembershipStatus.CANCELLED
        and m.ended_at
        and start <= m.ended_at <= end
    ]
    churn = _percent(len(cancelled), len(active) + len(cancelled))

    tier_counts = Counter(m.membership_tier.value for m in active)
    expiring_cutoff = datetime.now(UTC) + timedelta(days=14)
    expiring_soon = [
        m
        for m in memberships
        if m.ended_at and datetime.now(UTC) <= m.ended_at <= expiring_cutoff
    ]

    return MembershipHealthResponse(
        period=period,
        start_date=start.date(),
        end_date=end.date(),
        total_active_members=len(active),
        new_this_period=len(new_members),
        cancelled_this_period=len(cancelled),
        churn_rate_percent=churn,
        retention_rate_percent=round(100 - churn, 2),
        tier_breakdown=[
            {"tier": k, "count": v} for k, v in sorted(tier_counts.items())
        ],
        expiring_soon_member_count=len(expiring_soon),
    )


@router.get("/gyms/{gym_id}/class-performance", response_model=ClassPerformanceResponse)
def class_performance_report(
    gym_id: UUID,
    session: SessionDep,
    _staff: StaffGymDep,
    _role: None = RequireOwnerOrManager,
    period: str = Query(default="monthly"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    instructor_staff_id: UUID | None = Query(default=None),
    class_type: str | None = Query(default=None),
) -> ClassPerformanceResponse:
    start, end = _period_bounds(period, start_date, end_date)
    q = select(ClassSession).where(
        ClassSession.gym_id == gym_id,
        col(ClassSession.start_time) >= start,
        col(ClassSession.start_time) <= end,
    )
    sessions = session.exec(q).all()
    if instructor_staff_id:
        sessions = [s for s in sessions if s.instructor_staff_id == instructor_staff_id]
    if class_type:
        sessions = [s for s in sessions if class_type.lower() in s.title.lower()]

    bookings = session.exec(select(Booking).where(Booking.gym_id == gym_id)).all()
    by_session: dict[UUID, list[Booking]] = defaultdict(list)
    for b in bookings:
        by_session[b.session_id].append(b)

    items: list[ClassPerformanceItem] = []
    class_booking_totals: Counter[str] = Counter()
    underperforming: list[UUID] = []
    for s in sessions:
        bks = [
            b for b in by_session.get(s.id, []) if b.status != BookingStatus.CANCELLED
        ]
        booked_count = len(bks)
        checked_in_count = sum(1 for b in bks if b.status == BookingStatus.CHECKED_IN)
        fill = _percent(booked_count, s.capacity)
        attendance = _percent(checked_in_count, booked_count)
        no_show = _percent(max(booked_count - checked_in_count, 0), booked_count)
        if fill < 40:
            underperforming.append(s.id)
        class_booking_totals[s.title] += booked_count
        items.append(
            ClassPerformanceItem(
                session_id=s.id,
                class_name=s.title,
                instructor_staff_id=s.instructor_staff_id,
                fill_rate_percent=fill,
                attendance_rate_percent=attendance,
                no_show_rate_percent=no_show,
                bookings=booked_count,
                capacity=s.capacity,
            )
        )

    popular = [name for name, _n in class_booking_totals.most_common(5)]
    return ClassPerformanceResponse(
        period=period,
        start_date=start.date(),
        end_date=end.date(),
        items=items,
        popular_classes=popular,
        underperforming_sessions=underperforming,
    )


@router.get(
    "/gyms/{gym_id}/staff-performance", response_model=list[StaffPerformanceItem]
)
def staff_performance_report(
    gym_id: UUID,
    session: SessionDep,
    _staff: StaffGymDep,
    _role: None = RequireOwnerOrManager,
    period: str = Query(default="monthly"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    staff_member_id: UUID | None = Query(default=None),
    role: StaffRole | None = Query(default=None),
) -> list[StaffPerformanceItem]:
    start, end = _period_bounds(period, start_date, end_date)

    staff_list = session.exec(
        select(Staff).where(Staff.gym_id == gym_id, Staff.is_active)
    ).all()
    if staff_member_id:
        staff_list = [s for s in staff_list if s.id == staff_member_id]
    if role:
        staff_list = [s for s in staff_list if s.role == role]

    sessions = session.exec(
        select(ClassSession).where(
            ClassSession.gym_id == gym_id,
            col(ClassSession.start_time) >= start,
            col(ClassSession.start_time) <= end,
        )
    ).all()
    session_map: dict[UUID, list[ClassSession]] = defaultdict(list)
    for cs in sessions:
        if cs.instructor_staff_id:
            session_map[cs.instructor_staff_id].append(cs)

    bookings = session.exec(select(Booking).where(Booking.gym_id == gym_id)).all()
    by_session: dict[UUID, list[Booking]] = defaultdict(list)
    for b in bookings:
        by_session[b.session_id].append(b)

    out: list[StaffPerformanceItem] = []
    for s in staff_list:
        taught = session_map.get(s.id, [])
        fill_rates: list[float] = []
        total_hours = 0.0
        for cs in taught:
            total_hours += max((cs.end_time - cs.start_time).total_seconds() / 3600, 0)
            booked = len(
                [
                    b
                    for b in by_session.get(cs.id, [])
                    if b.status != BookingStatus.CANCELLED
                ]
            )
            fill_rates.append(_percent(booked, cs.capacity))
        avg_fill = round(sum(fill_rates) / len(fill_rates), 2) if fill_rates else 0.0
        earnings = (
            int(round(total_hours * s.hourly_rate_cents))
            if s.hourly_rate_cents is not None
            else None
        )
        out.append(
            StaffPerformanceItem(
                staff_id=s.id,
                full_name=f"{s.first_name} {s.last_name}".strip(),
                role=s.role.value,
                classes_taught=len(taught),
                avg_fill_rate_percent=avg_fill,
                total_hours_worked=round(total_hours, 2),
                estimated_earnings_cents=earnings,
            )
        )
    return out


@router.get("/me/class-history", response_model=ConsumerClassHistoryResponse)
def consumer_class_history(
    session: SessionDep,
    consumer: CurrentConsumer,
    gym_id: UUID | None = Query(default=None),
    class_type: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
) -> ConsumerClassHistoryResponse:
    bookings = session.exec(
        select(Booking).where(
            Booking.consumer_id == consumer.id,
            Booking.status == BookingStatus.CHECKED_IN,
        )
    ).all()
    sessions = {s.id: s for s in session.exec(select(ClassSession)).all()}
    rows = [(b, sessions[b.session_id]) for b in bookings if b.session_id in sessions]

    if gym_id:
        rows = [(b, s) for b, s in rows if s.gym_id == gym_id]
    if class_type:
        rows = [(b, s) for b, s in rows if class_type.lower() in s.title.lower()]
    if start_date:
        start_dt = datetime.combine(start_date, time.min, tzinfo=UTC)
        rows = [
            (b, s) for b, s in rows if b.checked_in_at and b.checked_in_at >= start_dt
        ]
    if end_date:
        end_dt = datetime.combine(end_date, time.max, tzinfo=UTC)
        rows = [
            (b, s) for b, s in rows if b.checked_in_at and b.checked_in_at <= end_dt
        ]

    instructors = {
        s.instructor_staff_id: session.get(Staff, s.instructor_staff_id)
        for _b, s in rows
        if s.instructor_staff_id
    }
    items: list[ConsumerClassHistoryItem] = []
    for b, s in rows:
        instructor_name: str | None = None
        if s.instructor_staff_id:
            inst = instructors.get(s.instructor_staff_id)
            if inst:
                instructor_name = f"{inst.first_name} {inst.last_name}".strip()
        items.append(
            ConsumerClassHistoryItem(
                session_id=s.id,
                class_name=s.title,
                gym_id=s.gym_id,
                instructor_name=instructor_name,
                attended_at=(b.checked_in_at or s.start_time),
            )
        )

    now = datetime.now(UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    month_count = sum(
        1 for b, _s in rows if b.checked_in_at and b.checked_in_at >= month_start
    )
    year_count = sum(
        1 for b, _s in rows if b.checked_in_at and b.checked_in_at >= year_start
    )

    return ConsumerClassHistoryResponse(
        items=items,
        total_attended_this_month=month_count,
        total_attended_this_year=year_count,
    )


@router.get("/me/stats", response_model=ConsumerStatsResponse)
def consumer_stats(
    session: SessionDep, consumer: CurrentConsumer
) -> ConsumerStatsResponse:
    bookings = session.exec(
        select(Booking).where(
            Booking.consumer_id == consumer.id,
            Booking.status == BookingStatus.CHECKED_IN,
        )
    ).all()
    sessions = {s.id: s for s in session.exec(select(ClassSession)).all()}
    rows = [(b, sessions[b.session_id]) for b in bookings if b.session_id in sessions]
    now = datetime.now(UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total = len(rows)
    month_total = sum(
        1 for b, _ in rows if b.checked_in_at and b.checked_in_at >= month_start
    )
    by_class = Counter(s.title for _b, s in rows)
    by_gym = Counter(str(s.gym_id) for _b, s in rows)

    week_set = {
        (
            (b.checked_in_at or s.start_time).isocalendar().year,
            (b.checked_in_at or s.start_time).isocalendar().week,
        )
        for b, s in rows
    }
    current_year, current_week, _ = now.isocalendar()
    streak = 0
    probe_year, probe_week = current_year, current_week
    while (probe_year, probe_week) in week_set:
        streak += 1
        probe_week -= 1
        if probe_week <= 0:
            probe_year -= 1
            probe_week = 52

    first_attended = min(
        ((b.checked_in_at or s.start_time) for b, s in rows), default=now
    )
    weeks_since_first = max(((now - first_attended).days // 7) + 1, 1)

    return ConsumerStatsResponse(
        total_classes_all_time=total,
        total_classes_this_month=month_total,
        favorite_class_type=by_class.most_common(1)[0][0] if by_class else None,
        most_visited_gym_id=UUID(by_gym.most_common(1)[0][0]) if by_gym else None,
        current_streak_weeks=streak,
        average_classes_per_week=round(total / weeks_since_first, 2) if total else 0.0,
    )


def _compute_at_risk_members(
    session: SessionDep,
    gym_id: UUID,
    inactivity_days: int = 14,
    drop_percent: float = 50.0,
) -> list[AtRiskMemberItem]:
    memberships = session.exec(
        select(GymMembership).where(
            GymMembership.gym_id == gym_id,
            GymMembership.status == GymMembershipStatus.ACTIVE,
        )
    ).all()

    now = datetime.now(UTC)
    flagged: list[AtRiskMemberItem] = []
    for m in memberships:
        check_ins = session.exec(
            select(CheckInRecord).where(
                CheckInRecord.gym_id == gym_id,
                CheckInRecord.consumer_id == m.consumer_id,
            )
        ).all()
        check_ins_sorted = sorted(
            check_ins, key=lambda c: c.checked_in_at, reverse=True
        )
        last = check_ins_sorted[0].checked_in_at if check_ins_sorted else None
        last_4_start = now - timedelta(days=28)
        prev_4_start = now - timedelta(days=56)
        recent = sum(1 for c in check_ins if c.checked_in_at >= last_4_start)
        previous = sum(
            1 for c in check_ins if prev_4_start <= c.checked_in_at < last_4_start
        )
        drop = _percent(max(previous - recent, 0), previous) if previous > 0 else 0.0
        inactive = (last is None) or ((now - last).days >= inactivity_days)
        declining = previous > 0 and drop >= drop_percent
        if inactive or declining:
            consumer = session.get(Consumer, m.consumer_id)
            if not consumer:
                continue
            flagged.append(
                AtRiskMemberItem(
                    consumer_id=consumer.id,
                    full_name=f"{consumer.first_name} {consumer.last_name}".strip(),
                    last_check_in_at=last,
                    days_since_last_check_in=(now - last).days if last else None,
                    recent_4_weeks_check_ins=recent,
                    previous_4_weeks_check_ins=previous,
                )
            )
    return flagged


@router.post("/gyms/{gym_id}/at-risk-members/run", response_model=AtRiskRunResponse)
def run_at_risk_detection(
    gym_id: UUID,
    session: SessionDep,
    _staff: StaffGymDep,
    _role: None = RequireOwnerOrManager,
    inactivity_days: int = Query(default=14, ge=1, le=120),
    drop_percent: float = Query(default=50.0, ge=1.0, le=100.0),
) -> AtRiskRunResponse:
    memberships = session.exec(
        select(GymMembership).where(
            GymMembership.gym_id == gym_id,
            GymMembership.status == GymMembershipStatus.ACTIVE,
        )
    ).all()
    flagged = _compute_at_risk_members(
        session, gym_id, inactivity_days=inactivity_days, drop_percent=drop_percent
    )
    return AtRiskRunResponse(
        gym_id=gym_id, evaluated_members=len(memberships), flagged_members=len(flagged)
    )


@router.get("/gyms/{gym_id}/at-risk-members", response_model=list[AtRiskMemberItem])
def at_risk_members(
    gym_id: UUID,
    session: SessionDep,
    _staff: StaffGymDep,
    _role: None = RequireOwnerOrManager,
    inactivity_days: int = Query(default=14, ge=1, le=120),
    drop_percent: float = Query(default=50.0, ge=1.0, le=100.0),
) -> list[AtRiskMemberItem]:
    return _compute_at_risk_members(
        session, gym_id, inactivity_days=inactivity_days, drop_percent=drop_percent
    )


@router.get("/gyms/{gym_id}/dashboard", response_model=GymOwnerDashboardResponse)
def gym_owner_dashboard(
    gym_id: UUID,
    session: SessionDep,
    _staff: StaffGymDep,
    _role: None = RequireOwnerOrManager,
) -> GymOwnerDashboardResponse:
    today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    now = datetime.now(UTC)

    failed_payments = session.exec(
        select(Payment).where(
            Payment.gym_id == gym_id,
            col(Payment.status).in_(
                [PaymentStatus.FAILED, PaymentStatus.FAILED_PERMANENT]
            ),
        )
    ).all()
    at_risk = _compute_at_risk_members(session, gym_id)
    sessions_today = session.exec(
        select(ClassSession).where(
            ClassSession.gym_id == gym_id,
            col(ClassSession.start_time) >= today_start,
            col(ClassSession.start_time) <= now + timedelta(days=1),
        )
    ).all()
    underperforming = [
        s
        for s in sessions_today
        if s.capacity > 0 and (s.spots_booked / s.capacity) < 0.4
    ]

    memberships = session.exec(
        select(GymMembership).where(GymMembership.gym_id == gym_id)
    ).all()
    expiring = [
        m
        for m in memberships
        if m.ended_at and now <= m.ended_at <= now + timedelta(days=14)
    ]

    today_revenue: int = int(
        session.exec(
            select(func.coalesce(func.sum(Payment.amount_cents), 0)).where(
                Payment.gym_id == gym_id,
                Payment.status == PaymentStatus.COMPLETED,
                col(Payment.completed_at).is_not(None),
                col(Payment.completed_at) >= today_start,
                col(Payment.completed_at) <= now,
            )
        ).one()
        or 0
    )

    today_check_ins = session.exec(
        select(CheckInRecord).where(
            CheckInRecord.gym_id == gym_id,
            col(CheckInRecord.checked_in_at) >= today_start,
            col(CheckInRecord.checked_in_at) <= now,
        )
    ).all()
    today_bookings = session.exec(
        select(Booking).where(
            Booking.gym_id == gym_id,
            col(Booking.created_at) >= today_start,
            col(Booking.created_at) <= now,
        )
    ).all()

    active_members = len(
        [m for m in memberships if m.status == GymMembershipStatus.ACTIVE]
    )
    fill_rates = [
        (s.spots_booked / s.capacity) * 100 for s in sessions_today if s.capacity > 0
    ]

    return GymOwnerDashboardResponse(
        gym_id=gym_id,
        action_items={
            "failed_payments": len(failed_payments),
            "at_risk_members": len(at_risk),
            "low_fill_classes": len(underperforming),
            "expiring_memberships": len(expiring),
        },
        today_summary={
            "revenue_cents": int(today_revenue),
            "check_ins": len(today_check_ins),
            "bookings": len(today_bookings),
        },
        quick_metrics={
            "active_members": active_members,
            "classes_today": len(sessions_today),
            "fill_rate_percent": round(sum(fill_rates) / len(fill_rates), 2)
            if fill_rates
            else 0.0,
        },
    )
