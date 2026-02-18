import subprocess
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import (
    Booking,
    CheckInRecord,
    ClassSession,
    Consumer,
    Gym,
    GymMembership,
    GymMessage,
    Item,
    MarketplaceSubscription,
    Notification,
    NotificationPreference,
    NotificationTemplate,
    Payment,
    PaymentReceipt,
    PaymentWebhookEvent,
    ReferralInvite,
    Space,
    Staff,
    User,
    WaitlistEntry,
)
from app.models.digital_waiver import DigitalWaiverAcceptance
from app.models.membership_plan import MembershipPlan
from app.seed import seed_all
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    subprocess.run(["uv", "run", "alembic", "upgrade", "head"], check=True)
    with Session(engine) as session:
        init_db(session)
        # Seed test data so gyms are available for all tests
        seed_all(session)
        yield session
        # Clean up in reverse dependency order (children before parents)
        session.execute(delete(Notification))
        session.execute(delete(NotificationPreference))
        session.execute(delete(NotificationTemplate))
        session.execute(delete(GymMessage))
        session.execute(delete(CheckInRecord))
        session.execute(delete(WaitlistEntry))
        session.execute(delete(Booking))
        session.execute(delete(DigitalWaiverAcceptance))
        session.execute(delete(ClassSession))
        session.execute(delete(Space))
        session.execute(delete(GymMembership))
        session.execute(delete(PaymentReceipt))
        session.execute(delete(PaymentWebhookEvent))
        session.execute(delete(Payment))
        session.execute(delete(ReferralInvite))
        session.execute(delete(MarketplaceSubscription))
        session.execute(delete(MembershipPlan))
        session.execute(delete(Staff))
        session.execute(delete(Consumer))
        session.execute(delete(Gym))
        session.execute(delete(Item))
        session.execute(delete(User))
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
