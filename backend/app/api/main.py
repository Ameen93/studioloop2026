import os

from fastapi import APIRouter

from app.api.routes import (
    admin,
    analytics,
    bookings,
    consumers,
    gyms,
    items,
    login,
    marketplace,
    notifications,
    payments,
    private,
    rbac_examples,
    realtime,
    staff_auth,
    staff_memberships,
    users,
    utils,
    webhooks,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(consumers.router)
api_router.include_router(gyms.router)
api_router.include_router(staff_auth.router)
api_router.include_router(staff_memberships.router)
api_router.include_router(bookings.router)
api_router.include_router(marketplace.router)
api_router.include_router(notifications.router)
api_router.include_router(analytics.router)
api_router.include_router(payments.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(rbac_examples.router)
api_router.include_router(admin.router)
api_router.include_router(webhooks.router)

# WebSocket routes are not supported on Vercel serverless
if not os.environ.get("VERCEL"):
    api_router.include_router(realtime.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
