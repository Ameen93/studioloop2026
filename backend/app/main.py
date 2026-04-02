from collections.abc import Awaitable, Callable

import sentry_sdk
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.routing import APIRoute
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlmodel import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.db import engine
from app.core.exception_handlers import register_exception_handlers
from app.core.rate_limit import limiter


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        if settings.ENVIRONMENT == "production":
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains; preload",
            )
        return response


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=(
        None
        if settings.ENVIRONMENT == "production"
        else f"{settings.API_V1_STR}/openapi.json"
    ),
    docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
    redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "Origin"],
    )

# Session middleware for OAuth state management (ARCH-14)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(SecurityHeadersMiddleware)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Register custom exception handlers for consistent error responses
register_exception_handlers(app)


@app.get("/health", tags=["health"])
async def liveness_check() -> dict[str, str]:
    """Liveness probe — confirms the process is running.

    Used by container orchestrators (Docker HEALTHCHECK, k8s livenessProbe).
    Does NOT check external dependencies so a transient DB outage
    won't cause unnecessary container restarts.
    """
    return {"status": "ok"}


@app.get("/ready", tags=["health"])
async def readiness_check() -> dict[str, str]:
    """Readiness probe — confirms the app can serve traffic.

    Checks database connectivity. Used by load balancers and deployment
    gates (k8s readinessProbe, Railway/Fly health checks for routing).
    Returns 503 if the database is unreachable.
    """
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={"status": "not ready", "db": "unreachable"},
        )
    return {"status": "ready", "db": "ok"}
