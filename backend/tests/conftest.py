import subprocess
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete, text

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import (
    Booking,
    CheckInRecord,
    ClassSession,
    ClassTemplate,
    Consumer,
    Gym,
    GymClosure,
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
    WebhookDelivery,
    WebhookEndpoint,
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
        # No explicit teardown cleanup: tests run against ephemeral/dev DB state and
        # cleanup has proven flaky due FK/lock ordering in session-scoped fixtures.
        pass


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
