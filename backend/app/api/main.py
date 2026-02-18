from fastapi import APIRouter

from app.api.routes import (
    bookings,
    consumers,
    gyms,
    items,
    login,
    marketplace,
    private,
    rbac_examples,
    staff_auth,
    staff_memberships,
    users,
    utils,
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
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(rbac_examples.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
