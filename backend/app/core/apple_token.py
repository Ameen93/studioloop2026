"""Apple ID token verification with JWKS signature validation.

Fetches Apple's public keys and verifies the JWT signature, audience,
and issuer before trusting any claims from the token.
"""

import logging
from typing import Any, cast

import jwt
from jwt import PyJWKClient

from app.core.config import settings

logger = logging.getLogger(__name__)

APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
APPLE_ISSUER = "https://appleid.apple.com"

_jwk_client = PyJWKClient(APPLE_JWKS_URL, cache_jwk_set=True, lifespan=3600)


def verify_apple_id_token(id_token: str) -> dict[str, Any]:
    """Decode and verify an Apple ID token using Apple's public JWKS.

    Args:
        id_token: The JWT id_token from Apple's OAuth response.

    Returns:
        The decoded token payload (dict with 'sub', 'email', etc.)

    Raises:
        jwt.PyJWTError: If signature verification, audience, or issuer fails.
    """
    signing_key = _jwk_client.get_signing_key_from_jwt(id_token)

    decoded = jwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.APPLE_CLIENT_ID,
        issuer=APPLE_ISSUER,
    )
    # jwt.decode is typed as returning Any; the claims are a JSON object.
    return cast(dict[str, Any], decoded)
