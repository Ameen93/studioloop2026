"""OAuth client configuration for social login (ARCH-14).

Uses Authlib for Google and Apple OAuth integration.
"""

import time

import jwt
from authlib.integrations.starlette_client import OAuth  # type: ignore[import-untyped]

from app.core.config import settings

# Initialize OAuth client
oauth = OAuth()

# Register Google OAuth client
# Only register if credentials are configured
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile",
        },
    )


def generate_apple_client_secret() -> str:
    """Generate Apple client secret JWT.

    Apple requires a JWT signed with ES256 algorithm using your private key.
    The JWT expires after 6 months maximum (Apple requirement).

    Returns:
        JWT string to use as client_secret for Apple OAuth.
    """
    headers = {
        "kid": settings.APPLE_KEY_ID,
        "alg": "ES256",
    }

    payload = {
        "iss": settings.APPLE_TEAM_ID,
        "iat": int(time.time()),
        "exp": int(time.time()) + (86400 * 180),  # 180 days max
        "aud": "https://appleid.apple.com",
        "sub": settings.APPLE_CLIENT_ID,
    }

    return jwt.encode(
        payload,
        settings.APPLE_PRIVATE_KEY,
        algorithm="ES256",
        headers=headers,
    )


# Register Apple OAuth client
# Apple requires manual configuration (no OpenID discovery)
if settings.APPLE_CLIENT_ID and settings.APPLE_PRIVATE_KEY:
    oauth.register(
        name="apple",
        client_id=settings.APPLE_CLIENT_ID,
        client_secret="",  # Generated dynamically per request
        authorize_url="https://appleid.apple.com/auth/authorize",
        access_token_url="https://appleid.apple.com/auth/token",
        client_kwargs={
            "scope": "name email",
            "response_mode": "form_post",  # Apple requires POST callback
        },
    )
