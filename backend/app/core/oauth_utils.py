"""OAuth redirect utilities.

Provides helpers for validating frontend redirect URIs and building
redirect responses with tokens in URL fragments (never sent to server logs).
"""

from urllib.parse import urlencode

from fastapi import HTTPException, status
from starlette.responses import RedirectResponse

from app.core.config import settings


def validate_oauth_redirect_uri(uri: str) -> str:
    """Validate that a redirect URI is in the allowlist.

    Args:
        uri: The redirect URI to validate

    Returns:
        The validated URI

    Raises:
        HTTPException: 400 if the URI is not in the allowlist
    """
    allowed = [
        u.strip() for u in settings.OAUTH_ALLOWED_REDIRECT_URIS.split(",") if u.strip()
    ]
    if uri not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_REDIRECT_URI",
                "message": "The provided redirect_uri is not allowed",
                "details": {},
            },
        )
    return uri


def build_oauth_redirect_response(redirect_uri: str, data: dict) -> RedirectResponse:
    """Build a redirect response with data encoded in the URL fragment.

    Uses URL fragment (#) so tokens never hit server logs.

    Args:
        redirect_uri: The frontend URL to redirect to
        data: Key-value pairs to encode in the fragment

    Returns:
        RedirectResponse with data in URL fragment
    """
    fragment = urlencode({k: v for k, v in data.items() if v is not None})
    return RedirectResponse(url=f"{redirect_uri}#{fragment}", status_code=302)
