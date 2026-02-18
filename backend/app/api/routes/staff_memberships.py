import secrets
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, select

from app.api.deps import (
    CurrentConsumer,
    CurrentStaff,
    RequireOwner,
    RequireOwnerOrManager,
    RequireStaff,
    SessionDep,
)
from app.core.security import get_password_hash
from app.models import (
    ClassSession,
    ClassSessionStatus,
    GymMembership,
    GymMembershipStatus,
    GymMembershipTier,
    Staff,
    StaffRole,
)
from app.models.digital_waiver import DigitalWaiverAcceptance
from app.models.membership_plan import (
    MembershipPlan,
    MembershipPlanCreate,
    MembershipPlanPublic,
    MembershipPlanUpdate,
)

router = APIRouter(prefix="/gyms", tags=["staff-memberships"])


class StaffCreateRequest(SQLModel):
    email: EmailStr = Field(max_length=255)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    role: StaffRole


class StaffRoleUpdateRequest(SQLModel):
    role: StaffRole


class StaffHoursUpdateRequest(SQLModel):
    working_hours: dict[str, dict[str, str | bool | None]]


class StaffPayRateUpdateRequest(SQLModel):
    hourly_rate_cents: int = Field(ge=0)


class StaffPublicResponse(SQLModel):
    id: UUID
    gym_id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None
    role: StaffRole
    invitation_status: str
    hourly_rate_cents: int | None
    working_hours: dict[str, dict[str, str | bool | None]]
    is_active: bool


class InstructorScheduleItem(SQLModel):
    class_session_id: UUID
    title: str
    start_time: datetime
    end_time: datetime


class InstructorEarningsResponse(SQLModel):
    instructor_staff_id: UUID
    hourly_rate_cents: int
    classes_taught: int
    estimated_earnings_cents: int


class MembershipPlanBenefitsUpdateRequest(SQLModel):
    benefits: list[str]


class MembershipPlanRulesUpdateRequest(SQLModel):
    rules: dict[str, int | bool | str]
    usage_limits: dict[str, int | bool | str]


class MembershipEnrollRequest(SQLModel):
    gym_id: UUID
    membership_plan_id: UUID
    payment_method_last4: str | None = Field(default=None, min_length=4, max_length=4)


class MembershipChangeRequest(SQLModel):
    membership_plan_id: UUID


class WaiverAcceptRequest(SQLModel):
    gym_membership_id: UUID
    waiver_version: str = Field(default="v1", min_length=1, max_length=50)


class MembershipPublic(SQLModel):
    id: UUID
    gym_id: UUID
    consumer_id: UUID
    membership_plan_id: UUID | None
    membership_tier: GymMembershipTier
    status: GymMembershipStatus
    payment_method_last4: str | None


class GymMemberListItem(SQLModel):
    membership_id: UUID
    consumer_id: UUID
    consumer_email: str
    membership_tier: GymMembershipTier
    status: GymMembershipStatus
    membership_plan_name: str | None


def _staff_public(staff: Staff) -> StaffPublicResponse:
    return StaffPublicResponse(
        id=staff.id,
        gym_id=staff.gym_id,
        email=staff.email,
        first_name=staff.first_name,
        last_name=staff.last_name,
        phone=staff.phone,
        role=staff.role,
        invitation_status=staff.invitation_status,
        hourly_rate_cents=staff.hourly_rate_cents,
        working_hours=staff.working_hours,
        is_active=staff.is_active,
    )


@router.get("/me/staff", response_model=list[StaffPublicResponse], dependencies=[RequireOwnerOrManager])
def list_staff(session: SessionDep, current_staff: CurrentStaff) -> list[StaffPublicResponse]:
    staff_list = session.exec(
        select(Staff).where(Staff.gym_id == current_staff.gym_id, Staff.is_active.is_(True)).order_by(Staff.created_at.asc())
    ).all()
    return [_staff_public(item) for item in staff_list]


@router.post("/me/staff", response_model=StaffPublicResponse, status_code=status.HTTP_201_CREATED, dependencies=[RequireOwnerOrManager])
def add_staff_member(session: SessionDep, current_staff: CurrentStaff, payload: StaffCreateRequest) -> StaffPublicResponse:
    if payload.role == StaffRole.MANAGER and current_staff.role != StaffRole.OWNER:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only owners can assign manager role", "details": {}})

    existing = session.exec(select(Staff).where(Staff.gym_id == current_staff.gym_id, Staff.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail={"code": "STAFF_ALREADY_EXISTS", "message": "Staff email already exists for this gym", "details": {}})

    existing_global = session.exec(select(Staff).where(Staff.email == payload.email, Staff.is_active.is_(True))).first()
    if existing_global:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "STAFF_EMAIL_ALREADY_EXISTS",
                "message": "Staff email already exists on the platform",
                "details": {},
            },
        )

    staff = Staff(
        gym_id=current_staff.gym_id,
        email=payload.email,
        hashed_password=get_password_hash(secrets.token_urlsafe(24)),
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        role=payload.role,
        is_email_verified=False,
        invitation_status="pending",
    )
    session.add(staff)
    session.commit()
    session.refresh(staff)
    return _staff_public(staff)


@router.patch("/me/staff/{staff_id}/role", response_model=StaffPublicResponse, dependencies=[RequireOwnerOrManager])
def update_staff_role(session: SessionDep, current_staff: CurrentStaff, staff_id: UUID, payload: StaffRoleUpdateRequest) -> StaffPublicResponse:
    staff = session.exec(select(Staff).where(Staff.id == staff_id, Staff.gym_id == current_staff.gym_id, Staff.is_active.is_(True))).first()
    if not staff:
        raise HTTPException(status_code=404, detail={"code": "STAFF_NOT_FOUND", "message": "Staff not found", "details": {}})
    if payload.role == StaffRole.MANAGER and current_staff.role != StaffRole.OWNER:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only owners can assign manager role", "details": {}})

    staff.role = payload.role
    session.add(staff)
    session.commit()
    session.refresh(staff)
    return _staff_public(staff)


@router.patch("/me/staff/{staff_id}/working_hours", response_model=StaffPublicResponse, dependencies=[RequireOwnerOrManager])
def update_staff_working_hours(session: SessionDep, current_staff: CurrentStaff, staff_id: UUID, payload: StaffHoursUpdateRequest) -> StaffPublicResponse:
    staff = session.exec(select(Staff).where(Staff.id == staff_id, Staff.gym_id == current_staff.gym_id, Staff.is_active.is_(True))).first()
    if not staff:
        raise HTTPException(status_code=404, detail={"code": "STAFF_NOT_FOUND", "message": "Staff not found", "details": {}})
    staff.working_hours = payload.working_hours
    session.add(staff)
    session.commit()
    session.refresh(staff)
    return _staff_public(staff)


@router.patch("/me/staff/{staff_id}/pay_rate", response_model=StaffPublicResponse, dependencies=[RequireOwnerOrManager])
def update_instructor_pay_rate(session: SessionDep, current_staff: CurrentStaff, staff_id: UUID, payload: StaffPayRateUpdateRequest) -> StaffPublicResponse:
    staff = session.exec(select(Staff).where(Staff.id == staff_id, Staff.gym_id == current_staff.gym_id, Staff.is_active.is_(True))).first()
    if not staff:
        raise HTTPException(status_code=404, detail={"code": "STAFF_NOT_FOUND", "message": "Staff not found", "details": {}})
    if staff.role != StaffRole.INSTRUCTOR:
        raise HTTPException(status_code=400, detail={"code": "INVALID_ROLE", "message": "Pay rate can only be set for instructors", "details": {}})
    staff.hourly_rate_cents = payload.hourly_rate_cents
    session.add(staff)
    session.commit()
    session.refresh(staff)
    return _staff_public(staff)


@router.get("/me/instructor/schedule", response_model=list[InstructorScheduleItem], dependencies=[RequireStaff])
def get_instructor_schedule(session: SessionDep, current_staff: CurrentStaff) -> list[InstructorScheduleItem]:
    if current_staff.role != StaffRole.INSTRUCTOR:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only instructors can view this schedule", "details": {}})

    classes = session.exec(
        select(ClassSession).where(
            ClassSession.gym_id == current_staff.gym_id,
            ClassSession.instructor_staff_id == current_staff.id,
            ClassSession.is_active.is_(True),
        ).order_by(ClassSession.start_time.asc())
    ).all()
    return [InstructorScheduleItem(class_session_id=c.id, title=c.title, start_time=c.start_time, end_time=c.end_time) for c in classes]


@router.get("/me/instructor/earnings", response_model=InstructorEarningsResponse, dependencies=[RequireStaff])
def get_instructor_earnings(session: SessionDep, current_staff: CurrentStaff) -> InstructorEarningsResponse:
    if current_staff.role != StaffRole.INSTRUCTOR:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only instructors can view earnings", "details": {}})
    hourly_rate = current_staff.hourly_rate_cents or 0
    classes = session.exec(
        select(ClassSession).where(
            ClassSession.gym_id == current_staff.gym_id,
            ClassSession.instructor_staff_id == current_staff.id,
            ClassSession.is_active.is_(True),
            ClassSession.status == ClassSessionStatus.SCHEDULED,
        )
    ).all()
    estimated = 0
    for c in classes:
        hours = max((c.end_time - c.start_time).total_seconds() / 3600, 0)
        estimated += int(hourly_rate * hours)

    return InstructorEarningsResponse(
        instructor_staff_id=current_staff.id,
        hourly_rate_cents=hourly_rate,
        classes_taught=len(classes),
        estimated_earnings_cents=estimated,
    )


@router.delete("/me/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireOwner])
def deactivate_staff_member(session: SessionDep, current_staff: CurrentStaff, staff_id: UUID) -> None:
    staff = session.exec(select(Staff).where(Staff.id == staff_id, Staff.gym_id == current_staff.gym_id, Staff.is_active.is_(True))).first()
    if not staff:
        raise HTTPException(status_code=404, detail={"code": "STAFF_NOT_FOUND", "message": "Staff not found", "details": {}})
    if staff.id == current_staff.id:
        raise HTTPException(status_code=400, detail={"code": "INVALID_ACTION", "message": "Owner cannot deactivate themselves", "details": {}})
    staff.soft_delete()
    session.add(staff)
    session.commit()


@router.post("/me/membership_plans", response_model=MembershipPlanPublic, status_code=status.HTTP_201_CREATED, dependencies=[RequireOwnerOrManager])
def create_membership_plan(session: SessionDep, current_staff: CurrentStaff, payload: MembershipPlanCreate) -> MembershipPlan:
    plan = MembershipPlan(gym_id=current_staff.gym_id, **payload.model_dump())
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


@router.patch("/me/membership_plans/{plan_id}", response_model=MembershipPlanPublic, dependencies=[RequireOwnerOrManager])
def update_membership_plan(session: SessionDep, current_staff: CurrentStaff, plan_id: UUID, payload: MembershipPlanUpdate) -> MembershipPlan:
    plan = session.exec(select(MembershipPlan).where(MembershipPlan.id == plan_id, MembershipPlan.gym_id == current_staff.gym_id, MembershipPlan.is_active.is_(True))).first()
    if not plan:
        raise HTTPException(status_code=404, detail={"code": "PLAN_NOT_FOUND", "message": "Membership plan not found", "details": {}})

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(plan, k, v)
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


@router.patch("/me/membership_plans/{plan_id}/benefits", response_model=MembershipPlanPublic, dependencies=[RequireOwnerOrManager])
def update_membership_plan_benefits(session: SessionDep, current_staff: CurrentStaff, plan_id: UUID, payload: MembershipPlanBenefitsUpdateRequest) -> MembershipPlan:
    return update_membership_plan(session, current_staff, plan_id, MembershipPlanUpdate(benefits=payload.benefits))


@router.patch("/me/membership_plans/{plan_id}/rules", response_model=MembershipPlanPublic, dependencies=[RequireOwnerOrManager])
def update_membership_plan_rules(session: SessionDep, current_staff: CurrentStaff, plan_id: UUID, payload: MembershipPlanRulesUpdateRequest) -> MembershipPlan:
    return update_membership_plan(
        session,
        current_staff,
        plan_id,
        MembershipPlanUpdate(rules=payload.rules, usage_limits=payload.usage_limits),
    )


@router.get("/{gym_slug}/membership_plans", response_model=list[MembershipPlanPublic])
def list_public_membership_plans(session: SessionDep, gym_slug: str) -> list[MembershipPlan]:
    from app.models import Gym

    gym = session.exec(select(Gym).where(Gym.slug == gym_slug.lower(), Gym.is_active.is_(True))).first()
    if not gym:
        raise HTTPException(status_code=404, detail={"code": "GYM_NOT_FOUND", "message": "Gym not found", "details": {}})
    return session.exec(select(MembershipPlan).where(MembershipPlan.gym_id == gym.id, MembershipPlan.is_active.is_(True))).all()


@router.post("/consumer/memberships", response_model=MembershipPublic, status_code=status.HTTP_201_CREATED)
def enroll_membership(session: SessionDep, current_consumer: CurrentConsumer, payload: MembershipEnrollRequest) -> MembershipPublic:
    plan = session.exec(select(MembershipPlan).where(MembershipPlan.id == payload.membership_plan_id, MembershipPlan.gym_id == payload.gym_id, MembershipPlan.is_active.is_(True))).first()
    if not plan:
        raise HTTPException(status_code=404, detail={"code": "PLAN_NOT_FOUND", "message": "Membership plan not found", "details": {}})

    existing_membership = session.exec(
        select(GymMembership).where(
            GymMembership.gym_id == payload.gym_id,
            GymMembership.consumer_id == current_consumer.id,
            GymMembership.is_active.is_(True),
            GymMembership.status == GymMembershipStatus.ACTIVE,
        )
    ).first()
    if existing_membership:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "ACTIVE_MEMBERSHIP_EXISTS",
                "message": "Consumer already has an active membership at this gym",
                "details": {},
            },
        )

    membership = GymMembership(
        gym_id=payload.gym_id,
        consumer_id=current_consumer.id,
        membership_plan_id=plan.id,
        membership_tier=plan.tier,
        status=GymMembershipStatus.ACTIVE,
        payment_method_last4=payload.payment_method_last4,
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return MembershipPublic(**membership.model_dump())


@router.get("/consumer/memberships", response_model=list[MembershipPublic])
def list_consumer_memberships(session: SessionDep, current_consumer: CurrentConsumer) -> list[MembershipPublic]:
    memberships = session.exec(select(GymMembership).where(GymMembership.consumer_id == current_consumer.id, GymMembership.is_active.is_(True)).order_by(GymMembership.created_at.desc())).all()
    return [MembershipPublic(**item.model_dump()) for item in memberships]


@router.get("/consumer/memberships/{membership_id}/benefits")
def get_membership_benefits(session: SessionDep, current_consumer: CurrentConsumer, membership_id: UUID) -> dict[str, object]:
    membership = session.exec(select(GymMembership).where(GymMembership.id == membership_id, GymMembership.consumer_id == current_consumer.id, GymMembership.is_active.is_(True))).first()
    if not membership:
        raise HTTPException(status_code=404, detail={"code": "MEMBERSHIP_NOT_FOUND", "message": "Membership not found", "details": {}})
    plan = session.get(MembershipPlan, membership.membership_plan_id) if membership.membership_plan_id else None
    return {
        "membership_id": str(membership.id),
        "benefits": (plan.benefits if plan else []),
        "usage_limits": (plan.usage_limits if plan else {}),
    }


@router.post("/consumer/memberships/{membership_id}/change", response_model=MembershipPublic)
def change_membership_plan(session: SessionDep, current_consumer: CurrentConsumer, membership_id: UUID, payload: MembershipChangeRequest) -> MembershipPublic:
    membership = session.exec(select(GymMembership).where(GymMembership.id == membership_id, GymMembership.consumer_id == current_consumer.id, GymMembership.is_active.is_(True))).first()
    if not membership:
        raise HTTPException(status_code=404, detail={"code": "MEMBERSHIP_NOT_FOUND", "message": "Membership not found", "details": {}})
    plan = session.exec(select(MembershipPlan).where(MembershipPlan.id == payload.membership_plan_id, MembershipPlan.gym_id == membership.gym_id, MembershipPlan.is_active.is_(True))).first()
    if not plan:
        raise HTTPException(status_code=404, detail={"code": "PLAN_NOT_FOUND", "message": "Membership plan not found", "details": {}})

    membership.membership_plan_id = plan.id
    membership.membership_tier = plan.tier
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return MembershipPublic(**membership.model_dump())


@router.post("/consumer/memberships/waiver_acceptance", status_code=status.HTTP_201_CREATED)
def accept_digital_waiver(session: SessionDep, current_consumer: CurrentConsumer, payload: WaiverAcceptRequest) -> dict[str, str]:
    membership = session.exec(select(GymMembership).where(GymMembership.id == payload.gym_membership_id, GymMembership.consumer_id == current_consumer.id, GymMembership.is_active.is_(True))).first()
    if not membership:
        raise HTTPException(status_code=404, detail={"code": "MEMBERSHIP_NOT_FOUND", "message": "Membership not found", "details": {}})

    acceptance = DigitalWaiverAcceptance(
        gym_id=membership.gym_id,
        consumer_id=current_consumer.id,
        gym_membership_id=membership.id,
        waiver_version=payload.waiver_version,
    )
    session.add(acceptance)
    session.commit()
    return {"message": "Waiver accepted"}


@router.get("/me/members", response_model=list[GymMemberListItem], dependencies=[RequireOwnerOrManager])
def list_gym_members(session: SessionDep, current_staff: CurrentStaff) -> list[GymMemberListItem]:
    from app.models import Consumer

    rows = session.exec(
        select(GymMembership, Consumer, MembershipPlan)
        .join(Consumer, Consumer.id == GymMembership.consumer_id)
        .outerjoin(MembershipPlan, MembershipPlan.id == GymMembership.membership_plan_id)
        .where(
            GymMembership.gym_id == current_staff.gym_id,
            GymMembership.is_active.is_(True),
        )
    ).all()

    return [
        GymMemberListItem(
            membership_id=membership.id,
            consumer_id=consumer.id,
            consumer_email=consumer.email,
            membership_tier=membership.membership_tier,
            status=membership.status,
            membership_plan_name=plan.name if plan else None,
        )
        for membership, consumer, plan in rows
    ]


@router.get("/me/members/{membership_id}", dependencies=[RequireOwnerOrManager])
def get_member_detail(session: SessionDep, current_staff: CurrentStaff, membership_id: UUID) -> dict[str, object]:
    from app.models import Consumer

    membership = session.exec(select(GymMembership).where(GymMembership.id == membership_id, GymMembership.gym_id == current_staff.gym_id, GymMembership.is_active.is_(True))).first()
    if not membership:
        raise HTTPException(status_code=404, detail={"code": "MEMBERSHIP_NOT_FOUND", "message": "Membership not found", "details": {}})
    consumer = session.get(Consumer, membership.consumer_id)
    plan = session.get(MembershipPlan, membership.membership_plan_id) if membership.membership_plan_id else None
    waivers = session.exec(select(DigitalWaiverAcceptance).where(DigitalWaiverAcceptance.gym_membership_id == membership.id)).all()

    return {
        "membership": MembershipPublic(**membership.model_dump()).model_dump(mode="json"),
        "consumer": {
            "id": str(consumer.id) if consumer else None,
            "email": consumer.email if consumer else None,
            "first_name": consumer.first_name if consumer else None,
            "last_name": consumer.last_name if consumer else None,
        },
        "plan": MembershipPlanPublic(**plan.model_dump()).model_dump(mode="json") if plan else None,
        "waiver_acceptances": [
            {"accepted_at": w.accepted_at.isoformat(), "waiver_version": w.waiver_version} for w in waivers
        ],
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }
