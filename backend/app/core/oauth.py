"""OAuth client configuration for social login (ARCH-14).

Uses Authlib for Google and Apple OAuth integration.
"""

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
