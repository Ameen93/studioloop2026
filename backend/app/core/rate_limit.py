"""Rate limiting configuration using slowapi.

Provides a configured limiter and per-endpoint rate limit constants.
Rate limiting is disabled in local environments (tests, development).

Uses X-Forwarded-For when behind a reverse proxy / load balancer,
falling back to the direct remote address for local development.
"""

from slowapi import Limiter
from starlette.requests import Request

from app.core.config import settings


def _get_real_client_ip(request: Request) -> str:
    """Extract the real client IP, respecting proxy headers.

    Behind a reverse proxy (nginx, Railway, Fly.io, CDN), the real
    client IP is in X-Forwarded-For. We take the first (leftmost)
    entry which is the original client before any intermediaries.
    Falls back to the direct connection address.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For: client, proxy1, proxy2 — take the first
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "127.0.0.1"


limiter = Limiter(
    key_func=_get_real_client_ip,
    enabled=settings.ENVIRONMENT != "local",
)

# Rate limit strings (per IP)
RATE_AUTH = "10/minute"
RATE_PASSWORD_RESET = "5/minute"
RATE_PAYMENT = "20/minute"
RATE_WEBHOOK = "60/minute"
RATE_DEFAULT = "120/minute"
