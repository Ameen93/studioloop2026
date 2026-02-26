"""Class scheduling endpoints (Epic 5).

Implements class templates CRUD, recurring scheduling, instructor assignment,
approval workflow, enhanced cancellation, capacity/pricing management,
and calendar views.
"""

from datetime import date, datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import field_validator, model_validator
from sqlalchemy import text
from sqlmodel import Field, SQLModel, col, select

from app.api.deps import (
    CurrentStaff,
    RequireOwnerOrManager,
    RequireStaff,
    SessionDep,
)
from app.models import (
    ClassSession,
    ClassSessionStatus,
    ClassTemplate,
    Space,
    Staff,
    StaffRole,
)
from app.models.class_session import ApprovalStatus
from app.models.class_template import ClassType

router = APIRouter(prefix="/gyms", tags=["class-scheduling"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class ClassTemplateCreateRequest(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    default_duration_minutes: int = Field(default=60, ge=5, le=480)
    default_capacity: int = Field(default=20, ge=1)
    class_type: ClassType = Field(default=ClassType.OTHER)
    default_instructor_staff_id: UUID | None = None
    default_space_id: UUID | None = None
    default_price_cents: int = Field(default=0, ge=0)
    waitlist_enabled: bool = Field(default=True)
    color: str = Field(default="#3B82F6", max_length=7)

    @field_validator("color")
    @classmethod
    def validate_color_hex(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("color must be a 7-char hex string like #3B82F6")
        return v


class ClassTemplateUpdateRequest(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    default_duration_minutes: int | None = Field(default=None, ge=5, le=480)
    default_capacity: int | None = Field(default=None, ge=1)
    class_type: ClassType | None = None
    default_instructor_staff_id: UUID | None = None
    default_space_id: UUID | None = None
    default_price_cents: int | None = Field(default=None, ge=0)
    waitlist_enabled: bool | None = None
    color: str | None = Field(default=None, max_length=7)


class ClassTemplateResponse(SQLModel):
    id: UUID
    gym_id: UUID
    name: str
    description: str | None
    default_duration_minutes: int
    default_capacity: int
    class_type: ClassType
    default_instructor_staff_id: UUID | None
    default_space_id: UUID | None
    default_price_cents: int
    waitlist_enabled: bool
    color: str
    is_active: bool


class ClassSessionFullResponse(SQLModel):
    id: UUID
    gym_id: UUID
    space_id: UUID
    instructor_staff_id: UUID | None
    title: str
    description: str | None
    class_type: ClassType | None
    start_time: datetime
    end_time: datetime
    status: str
    capacity: int
    spots_booked: int
    waitlist_enabled: bool
    waitlist_capacity: int
    price_cents: int
    class_template_id: UUID | None
    recurrence_group_id: UUID | None
    approval_status: str
    created_by_staff_id: UUID | None
    cancellation_reason: str | None
    cancelled_by_staff_id: UUID | None
    marketplace_visible: bool


class ClassSessionCreateRequest(SQLModel):
    space_id: UUID
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    class_type: ClassType | None = None
    start_time: datetime
    end_time: datetime
    capacity: int = Field(default=20, ge=0)
    price_cents: int = Field(default=0, ge=0)
    instructor_staff_id: UUID | None = None
    class_template_id: UUID | None = None
    waitlist_enabled: bool = Field(default=True)
    waitlist_capacity: int = Field(default=0, ge=0)
    marketplace_visible: bool = Field(default=True)

    @model_validator(mode="after")
    def validate_time_window(self) -> "ClassSessionCreateRequest":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class RecurringScheduleRequest(SQLModel):
    space_id: UUID
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    class_type: ClassType | None = None
    start_date: date
    end_date: date
    days_of_week: list[int] = Field(min_length=1)
    start_time_hour: int = Field(ge=0, le=23)
    start_time_minute: int = Field(ge=0, le=59)
    duration_minutes: int = Field(ge=5, le=480)
    capacity: int = Field(default=20, ge=0)
    price_cents: int = Field(default=0, ge=0)
    instructor_staff_id: UUID | None = None
    class_template_id: UUID | None = None
    waitlist_enabled: bool = Field(default=True)
    waitlist_capacity: int = Field(default=0, ge=0)
    marketplace_visible: bool = Field(default=True)

    @field_validator("days_of_week")
    @classmethod
    def validate_days(cls, v: list[int]) -> list[int]:
        for d in v:
            if d < 0 or d > 6:
                raise ValueError("days_of_week values must be 0-6 (Mon=0)")
        return sorted(set(v))

    @model_validator(mode="after")
    def validate_date_range(self) -> "RecurringScheduleRequest":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        if (self.end_date - self.start_date).days > 365:
            raise ValueError("recurrence range cannot exceed 365 days")
        return self


class RecurringScheduleResponse(SQLModel):
    recurrence_group_id: UUID
    created_count: int
    skipped_conflicts: int
    sessions: list[ClassSessionFullResponse]


class InstructorAssignRequest(SQLModel):
    instructor_staff_id: UUID | None


class ApprovalActionRequest(SQLModel):
    approval_status: ApprovalStatus

    @field_validator("approval_status")
    @classmethod
    def validate_status(cls, v: ApprovalStatus) -> ApprovalStatus:
        if v not in (ApprovalStatus.APPROVED, ApprovalStatus.REJECTED):
            raise ValueError("Must be 'approved' or 'rejected'")
        return v


class CancelRequest(SQLModel):
    reason: str | None = Field(default=None, max_length=500)


class CancelResponse(SQLModel):
    id: UUID
    status: str
    cancellation_reason: str | None
    cancelled_by_staff_id: UUID | None
    booking_count: int


class CapacityUpdateRequest(SQLModel):
    capacity: int = Field(ge=0)
    waitlist_capacity: int | None = Field(default=None, ge=0)


class PricingUpdateRequest(SQLModel):
    price_cents: int = Field(ge=0)
    marketplace_visible: bool | None = None


class CalendarSessionItem(SQLModel):
    id: UUID
    space_id: UUID
    instructor_staff_id: UUID | None
    title: str
    class_type: ClassType | None
    start_time: datetime
    end_time: datetime
    status: str
    capacity: int
    spots_booked: int
    price_cents: int
    approval_status: str
    color: str | None = None


class CalendarDayGroup(SQLModel):
    date: date
    sessions: list[CalendarSessionItem]


# ---------------------------------------------------------------------------
# Helper to serialize a ClassSession -> ClassSessionFullResponse
# ---------------------------------------------------------------------------


def _serialize_session(cs: ClassSession) -> ClassSessionFullResponse:
    return ClassSessionFullResponse(
        id=cs.id,
        gym_id=cs.gym_id,
        space_id=cs.space_id,
        instructor_staff_id=cs.instructor_staff_id,
        title=cs.title,
        description=cs.description,
        class_type=cs.class_type,
        start_time=cs.start_time,
        end_time=cs.end_time,
        status=cs.status.value,
        capacity=cs.capacity,
        spots_booked=cs.spots_booked,
        waitlist_enabled=cs.waitlist_enabled,
        waitlist_capacity=cs.waitlist_capacity,
        price_cents=cs.price_cents,
        class_template_id=cs.class_template_id,
        recurrence_group_id=cs.recurrence_group_id,
        approval_status=cs.approval_status.value,
        created_by_staff_id=cs.created_by_staff_id,
        cancellation_reason=cs.cancellation_reason,
        cancelled_by_staff_id=cs.cancelled_by_staff_id,
        marketplace_visible=cs.marketplace_visible,
    )


def _get_active_session(session, class_session_id: UUID, gym_id: UUID) -> ClassSession:
    cs = session.exec(
        select(ClassSession).where(
            ClassSession.id == class_session_id,
            ClassSession.gym_id == gym_id,
            col(ClassSession.is_active).is_(True),
        )
    ).first()
    if not cs:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "CLASS_SESSION_NOT_FOUND",
                "message": "Class session not found",
                "details": {},
            },
        )
    return cs


def _check_space_exists(session, space_id: UUID, gym_id: UUID) -> Space:
    space = session.exec(
        select(Space).where(
            Space.id == space_id,
            Space.gym_id == gym_id,
            col(Space.is_active).is_(True),
        )
    ).first()
    if not space:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "SPACE_NOT_FOUND",
                "message": "Space not found",
                "details": {},
            },
        )
    return space


def _has_space_conflict(
    session,
    gym_id: UUID,
    space_id: UUID,
    start: datetime,
    end: datetime,
    exclude_id: UUID | None = None,
) -> bool:
    q = select(ClassSession.id).where(
        ClassSession.gym_id == gym_id,
        ClassSession.space_id == space_id,
        col(ClassSession.is_active).is_(True),
        ClassSession.status != ClassSessionStatus.CANCELLED,
        start < ClassSession.end_time,
        end > ClassSession.start_time,
    )
    if exclude_id:
        q = q.where(ClassSession.id != exclude_id)
    return session.exec(q).first() is not None


def _has_instructor_conflict(
    session,
    gym_id: UUID,
    instructor_id: UUID,
    start: datetime,
    end: datetime,
    exclude_id: UUID | None = None,
) -> bool:
    q = select(ClassSession.id).where(
        ClassSession.gym_id == gym_id,
        ClassSession.instructor_staff_id == instructor_id,
        col(ClassSession.is_active).is_(True),
        ClassSession.status != ClassSessionStatus.CANCELLED,
        start < ClassSession.end_time,
        end > ClassSession.start_time,
    )
    if exclude_id:
        q = q.where(ClassSession.id != exclude_id)
    return session.exec(q).first() is not None


# ---------------------------------------------------------------------------
# 1. ClassTemplate CRUD
# ---------------------------------------------------------------------------


@router.post(
    "/me/class_templates",
    response_model=ClassTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireOwnerOrManager],
)
def create_class_template(
    session: SessionDep,
    current_staff: CurrentStaff,
    payload: ClassTemplateCreateRequest,
) -> ClassTemplateResponse:
    if payload.default_space_id:
        _check_space_exists(session, payload.default_space_id, current_staff.gym_id)

    template = ClassTemplate(
        gym_id=current_staff.gym_id,
        **payload.model_dump(),
    )
    session.add(template)
    session.commit()
    session.refresh(template)
    return ClassTemplateResponse.model_validate(template)


@router.get(
    "/me/class_templates",
    response_model=list[ClassTemplateResponse],
    dependencies=[RequireStaff],
)
def list_class_templates(
    session: SessionDep,
    current_staff: CurrentStaff,
) -> list[ClassTemplateResponse]:
    templates = session.exec(
        select(ClassTemplate).where(
            ClassTemplate.gym_id == current_staff.gym_id,
            col(ClassTemplate.is_active).is_(True),
        )
    ).all()
    return [ClassTemplateResponse.model_validate(t) for t in templates]


@router.get(
    "/me/class_templates/{template_id}",
    response_model=ClassTemplateResponse,
    dependencies=[RequireStaff],
)
def get_class_template(
    session: SessionDep,
    current_staff: CurrentStaff,
    template_id: UUID,
) -> ClassTemplateResponse:
    template = session.exec(
        select(ClassTemplate).where(
            ClassTemplate.id == template_id,
            ClassTemplate.gym_id == current_staff.gym_id,
            col(ClassTemplate.is_active).is_(True),
        )
    ).first()
    if not template:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "CLASS_TEMPLATE_NOT_FOUND",
                "message": "Class template not found",
                "details": {},
            },
        )
    return ClassTemplateResponse.model_validate(template)


@router.patch(
    "/me/class_templates/{template_id}",
    response_model=ClassTemplateResponse,
    dependencies=[RequireOwnerOrManager],
)
def update_class_template(
    session: SessionDep,
    current_staff: CurrentStaff,
    template_id: UUID,
    payload: ClassTemplateUpdateRequest,
) -> ClassTemplateResponse:
    template = session.exec(
        select(ClassTemplate).where(
            ClassTemplate.id == template_id,
            ClassTemplate.gym_id == current_staff.gym_id,
            col(ClassTemplate.is_active).is_(True),
        )
    ).first()
    if not template:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "CLASS_TEMPLATE_NOT_FOUND",
                "message": "Class template not found",
                "details": {},
            },
        )

    update_data = payload.model_dump(exclude_unset=True)
    if "default_space_id" in update_data and update_data["default_space_id"]:
        _check_space_exists(
            session, update_data["default_space_id"], current_staff.gym_id
        )

    for key, value in update_data.items():
        setattr(template, key, value)

    session.add(template)
    session.commit()
    session.refresh(template)
    return ClassTemplateResponse.model_validate(template)


@router.delete(
    "/me/class_templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[RequireOwnerOrManager],
)
def delete_class_template(
    session: SessionDep,
    current_staff: CurrentStaff,
    template_id: UUID,
) -> None:
    template = session.exec(
        select(ClassTemplate).where(
            ClassTemplate.id == template_id,
            ClassTemplate.gym_id == current_staff.gym_id,
            col(ClassTemplate.is_active).is_(True),
        )
    ).first()
    if not template:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "CLASS_TEMPLATE_NOT_FOUND",
                "message": "Class template not found",
                "details": {},
            },
        )

    template.soft_delete()
    session.add(template)
    session.commit()


# ---------------------------------------------------------------------------
# 2. Enhanced class session create (replaces the basic one in gyms.py)
# ---------------------------------------------------------------------------


@router.post(
    "/me/class_sessions",
    response_model=ClassSessionFullResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireStaff],
)
def create_class_session(
    session: SessionDep,
    current_staff: CurrentStaff,
    payload: ClassSessionCreateRequest,
) -> ClassSessionFullResponse:
    _check_space_exists(session, payload.space_id, current_staff.gym_id)

    # Advisory lock on space to prevent double-booking
    session.execute(
        text("SELECT pg_advisory_xact_lock(hashtext(:space_key))"),
        {"space_key": str(payload.space_id)},
    )

    if _has_space_conflict(
        session,
        current_staff.gym_id,
        payload.space_id,
        payload.start_time,
        payload.end_time,
    ):
        raise HTTPException(
            status_code=409,
            detail={
                "code": "SPACE_TIME_CONFLICT",
                "message": "The selected space is already booked for the requested time.",
                "details": {},
            },
        )

    # Instructor conflict check
    if payload.instructor_staff_id and _has_instructor_conflict(
        session,
        current_staff.gym_id,
        payload.instructor_staff_id,
        payload.start_time,
        payload.end_time,
    ):
        raise HTTPException(
            status_code=409,
            detail={
                "code": "INSTRUCTOR_TIME_CONFLICT",
                "message": "The instructor has another class at the requested time.",
                "details": {},
            },
        )

    # Determine approval status based on role
    if current_staff.role in (StaffRole.OWNER, StaffRole.MANAGER):
        approval = ApprovalStatus.AUTO_APPROVED
    else:
        approval = ApprovalStatus.PENDING_APPROVAL

    cs = ClassSession(
        gym_id=current_staff.gym_id,
        space_id=payload.space_id,
        title=payload.title,
        description=payload.description,
        class_type=payload.class_type,
        start_time=payload.start_time,
        end_time=payload.end_time,
        capacity=payload.capacity,
        price_cents=payload.price_cents,
        instructor_staff_id=payload.instructor_staff_id,
        class_template_id=payload.class_template_id,
        waitlist_enabled=payload.waitlist_enabled,
        waitlist_capacity=payload.waitlist_capacity,
        marketplace_visible=payload.marketplace_visible,
        approval_status=approval,
        created_by_staff_id=current_staff.id,
    )
    session.add(cs)
    session.commit()
    session.refresh(cs)
    return _serialize_session(cs)


# ---------------------------------------------------------------------------
# 3. Recurring scheduling
# ---------------------------------------------------------------------------


@router.post(
    "/me/class_sessions/recurring",
    response_model=RecurringScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireOwnerOrManager],
)
def create_recurring_sessions(
    session: SessionDep,
    current_staff: CurrentStaff,
    payload: RecurringScheduleRequest,
) -> RecurringScheduleResponse:
    _check_space_exists(session, payload.space_id, current_staff.gym_id)

    recurrence_group_id = uuid4()
    created: list[ClassSession] = []
    skipped = 0

    current_date = payload.start_date
    while current_date <= payload.end_date:
        if current_date.weekday() in payload.days_of_week:
            start_dt = datetime(
                current_date.year,
                current_date.month,
                current_date.day,
                payload.start_time_hour,
                payload.start_time_minute,
                tzinfo=timezone.utc,
            )
            end_dt = start_dt + timedelta(minutes=payload.duration_minutes)

            # Skip if space conflict
            if _has_space_conflict(
                session,
                current_staff.gym_id,
                payload.space_id,
                start_dt,
                end_dt,
            ):
                skipped += 1
                current_date += timedelta(days=1)
                continue

            # Skip if instructor conflict
            if payload.instructor_staff_id and _has_instructor_conflict(
                session,
                current_staff.gym_id,
                payload.instructor_staff_id,
                start_dt,
                end_dt,
            ):
                skipped += 1
                current_date += timedelta(days=1)
                continue

            cs = ClassSession(
                gym_id=current_staff.gym_id,
                space_id=payload.space_id,
                title=payload.title,
                description=payload.description,
                class_type=payload.class_type,
                start_time=start_dt,
                end_time=end_dt,
                capacity=payload.capacity,
                price_cents=payload.price_cents,
                instructor_staff_id=payload.instructor_staff_id,
                class_template_id=payload.class_template_id,
                waitlist_enabled=payload.waitlist_enabled,
                waitlist_capacity=payload.waitlist_capacity,
                marketplace_visible=payload.marketplace_visible,
                recurrence_group_id=recurrence_group_id,
                approval_status=ApprovalStatus.AUTO_APPROVED,
                created_by_staff_id=current_staff.id,
            )
            session.add(cs)
            created.append(cs)

        current_date += timedelta(days=1)

    session.commit()
    for cs in created:
        session.refresh(cs)

    return RecurringScheduleResponse(
        recurrence_group_id=recurrence_group_id,
        created_count=len(created),
        skipped_conflicts=skipped,
        sessions=[_serialize_session(cs) for cs in created],
    )


# ---------------------------------------------------------------------------
# 4. Instructor assignment with conflict check
# ---------------------------------------------------------------------------


@router.patch(
    "/me/class_sessions/{class_session_id}/instructor",
    response_model=ClassSessionFullResponse,
    dependencies=[RequireOwnerOrManager],
)
def assign_instructor(
    session: SessionDep,
    current_staff: CurrentStaff,
    class_session_id: UUID,
    payload: InstructorAssignRequest,
) -> ClassSessionFullResponse:
    cs = _get_active_session(session, class_session_id, current_staff.gym_id)

    if payload.instructor_staff_id:
        # Verify the instructor exists and belongs to this gym
        instructor = session.exec(
            select(Staff).where(
                Staff.id == payload.instructor_staff_id,
                Staff.gym_id == current_staff.gym_id,
            )
        ).first()
        if not instructor:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "STAFF_NOT_FOUND",
                    "message": "Instructor not found in this gym",
                    "details": {},
                },
            )

        # Conflict check
        if _has_instructor_conflict(
            session,
            current_staff.gym_id,
            payload.instructor_staff_id,
            cs.start_time,
            cs.end_time,
            exclude_id=cs.id,
        ):
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "INSTRUCTOR_TIME_CONFLICT",
                    "message": "The instructor has another class at the same time.",
                    "details": {},
                },
            )

    cs.instructor_staff_id = payload.instructor_staff_id
    session.add(cs)
    session.commit()
    session.refresh(cs)
    return _serialize_session(cs)


# ---------------------------------------------------------------------------
# 5. Approval workflow
# ---------------------------------------------------------------------------


@router.get(
    "/me/class_sessions/pending",
    response_model=list[ClassSessionFullResponse],
    dependencies=[RequireOwnerOrManager],
)
def list_pending_sessions(
    session: SessionDep,
    current_staff: CurrentStaff,
) -> list[ClassSessionFullResponse]:
    sessions_list = session.exec(
        select(ClassSession)
        .where(
            ClassSession.gym_id == current_staff.gym_id,
            col(ClassSession.is_active).is_(True),
            ClassSession.approval_status == ApprovalStatus.PENDING_APPROVAL,
        )
        .order_by(ClassSession.start_time)
    ).all()
    return [_serialize_session(cs) for cs in sessions_list]


@router.patch(
    "/me/class_sessions/{class_session_id}/approval",
    response_model=ClassSessionFullResponse,
    dependencies=[RequireOwnerOrManager],
)
def update_approval(
    session: SessionDep,
    current_staff: CurrentStaff,
    class_session_id: UUID,
    payload: ApprovalActionRequest,
) -> ClassSessionFullResponse:
    cs = _get_active_session(session, class_session_id, current_staff.gym_id)

    if cs.approval_status not in (
        ApprovalStatus.PENDING_APPROVAL,
        ApprovalStatus.APPROVED,
        ApprovalStatus.REJECTED,
    ):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_APPROVAL_TRANSITION",
                "message": "Cannot change approval status of auto-approved sessions",
                "details": {},
            },
        )

    cs.approval_status = payload.approval_status
    session.add(cs)
    session.commit()
    session.refresh(cs)
    return _serialize_session(cs)


# ---------------------------------------------------------------------------
# 6. Enhanced cancellation
# ---------------------------------------------------------------------------


@router.post(
    "/me/class_sessions/{class_session_id}/cancel",
    response_model=CancelResponse,
    dependencies=[RequireOwnerOrManager],
)
def cancel_class_session(
    session: SessionDep,
    current_staff: CurrentStaff,
    class_session_id: UUID,
    payload: CancelRequest | None = None,
) -> CancelResponse:
    cs = _get_active_session(session, class_session_id, current_staff.gym_id)

    if cs.status == ClassSessionStatus.CANCELLED:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "ALREADY_CANCELLED",
                "message": "This class session is already cancelled",
                "details": {},
            },
        )

    cs.status = ClassSessionStatus.CANCELLED
    cs.cancelled_by_staff_id = current_staff.id
    if payload and payload.reason:
        cs.cancellation_reason = payload.reason

    session.add(cs)
    session.commit()
    session.refresh(cs)

    return CancelResponse(
        id=cs.id,
        status=cs.status.value,
        cancellation_reason=cs.cancellation_reason,
        cancelled_by_staff_id=cs.cancelled_by_staff_id,
        booking_count=cs.spots_booked,
    )


# ---------------------------------------------------------------------------
# 7. Capacity management
# ---------------------------------------------------------------------------


@router.patch(
    "/me/class_sessions/{class_session_id}/capacity",
    response_model=ClassSessionFullResponse,
    dependencies=[RequireOwnerOrManager],
)
def update_capacity(
    session: SessionDep,
    current_staff: CurrentStaff,
    class_session_id: UUID,
    payload: CapacityUpdateRequest,
) -> ClassSessionFullResponse:
    cs = _get_active_session(session, class_session_id, current_staff.gym_id)

    cs.capacity = payload.capacity
    if payload.waitlist_capacity is not None:
        cs.waitlist_capacity = payload.waitlist_capacity

    session.add(cs)
    session.commit()
    session.refresh(cs)
    return _serialize_session(cs)


# ---------------------------------------------------------------------------
# 8. Marketplace pricing
# ---------------------------------------------------------------------------


@router.patch(
    "/me/class_sessions/{class_session_id}/pricing",
    response_model=ClassSessionFullResponse,
    dependencies=[RequireOwnerOrManager],
)
def update_pricing(
    session: SessionDep,
    current_staff: CurrentStaff,
    class_session_id: UUID,
    payload: PricingUpdateRequest,
) -> ClassSessionFullResponse:
    cs = _get_active_session(session, class_session_id, current_staff.gym_id)

    cs.price_cents = payload.price_cents
    if payload.marketplace_visible is not None:
        cs.marketplace_visible = payload.marketplace_visible

    session.add(cs)
    session.commit()
    session.refresh(cs)
    return _serialize_session(cs)


# ---------------------------------------------------------------------------
# 9. Calendar endpoint
# ---------------------------------------------------------------------------


@router.get(
    "/me/class_sessions/calendar",
    response_model=list[CalendarDayGroup],
    dependencies=[RequireStaff],
)
def get_calendar(
    session: SessionDep,
    current_staff: CurrentStaff,
    start_date: date = Query(...),
    end_date: date = Query(...),
    space_id: UUID | None = Query(default=None),
    instructor_staff_id: UUID | None = Query(default=None),
    class_type: ClassType | None = Query(default=None),
    status_filter: ClassSessionStatus | None = Query(default=None, alias="status"),
) -> list[CalendarDayGroup]:
    if (end_date - start_date).days > 90:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "DATE_RANGE_TOO_LARGE",
                "message": "Calendar range cannot exceed 90 days",
                "details": {},
            },
        )

    start_dt = datetime(
        start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc
    )
    end_dt = datetime(
        end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=timezone.utc
    )

    q = select(ClassSession).where(
        ClassSession.gym_id == current_staff.gym_id,
        col(ClassSession.is_active).is_(True),
        ClassSession.start_time >= start_dt,
        ClassSession.start_time <= end_dt,
    )

    if space_id:
        q = q.where(ClassSession.space_id == space_id)
    if instructor_staff_id:
        q = q.where(ClassSession.instructor_staff_id == instructor_staff_id)
    if class_type:
        q = q.where(ClassSession.class_type == class_type)
    if status_filter:
        q = q.where(ClassSession.status == status_filter)

    q = q.order_by(ClassSession.start_time)
    sessions_list = session.exec(q).all()

    # Look up template colors for sessions that have a template
    template_ids = {
        cs.class_template_id for cs in sessions_list if cs.class_template_id
    }
    color_map: dict[UUID, str] = {}
    if template_ids:
        templates = session.exec(
            select(ClassTemplate).where(col(ClassTemplate.id).in_(template_ids))
        ).all()
        color_map = {t.id: t.color for t in templates}

    # Group by date
    groups: dict[date, list[CalendarSessionItem]] = {}
    for cs in sessions_list:
        d = cs.start_time.date()
        item = CalendarSessionItem(
            id=cs.id,
            space_id=cs.space_id,
            instructor_staff_id=cs.instructor_staff_id,
            title=cs.title,
            class_type=cs.class_type,
            start_time=cs.start_time,
            end_time=cs.end_time,
            status=cs.status.value,
            capacity=cs.capacity,
            spots_booked=cs.spots_booked,
            price_cents=cs.price_cents,
            approval_status=cs.approval_status.value,
            color=color_map.get(cs.class_template_id) if cs.class_template_id else None,
        )
        groups.setdefault(d, []).append(item)

    return [
        CalendarDayGroup(date=d, sessions=items) for d, items in sorted(groups.items())
    ]


# ---------------------------------------------------------------------------
# List class sessions (basic)
# ---------------------------------------------------------------------------


@router.get(
    "/me/class_sessions",
    response_model=list[ClassSessionFullResponse],
    dependencies=[RequireStaff],
)
def list_class_sessions(
    session: SessionDep,
    current_staff: CurrentStaff,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[ClassSessionFullResponse]:
    sessions_list = session.exec(
        select(ClassSession)
        .where(
            ClassSession.gym_id == current_staff.gym_id,
            col(ClassSession.is_active).is_(True),
        )
        .order_by(ClassSession.start_time.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return [_serialize_session(cs) for cs in sessions_list]


@router.get(
    "/me/class_sessions/{class_session_id}",
    response_model=ClassSessionFullResponse,
    dependencies=[RequireStaff],
)
def get_class_session(
    session: SessionDep,
    current_staff: CurrentStaff,
    class_session_id: UUID,
) -> ClassSessionFullResponse:
    cs = _get_active_session(session, class_session_id, current_staff.gym_id)
    return _serialize_session(cs)
