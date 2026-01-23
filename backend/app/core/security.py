"""Security utilities for authentication.

Per ARCH-11: Password hashing uses Argon2 via pwdlib.
Backward compatibility is maintained for legacy bcrypt hashes.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext
from pwdlib import PasswordHash

from app.core.config import settings

# Argon2 hasher for new passwords (ARCH-11)
password_hasher = PasswordHash.recommended()

# Legacy bcrypt context for backward compatibility with existing users
_legacy_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """Create a JWT access token.

    Args:
        subject: The token subject (typically user ID)
        expires_delta: Token validity duration

    Returns:
        Encoded JWT token string
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str | Any, expires_delta: timedelta) -> str:
    """Create a JWT refresh token (ARCH-12).

    Refresh tokens have longer expiry and include a type claim
    to differentiate from access tokens.

    Args:
        subject: The token subject (typically user ID)
        expires_delta: Token validity duration

    Returns:
        Encoded JWT refresh token string
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.

    Supports both Argon2 (new) and bcrypt (legacy) hashes for backward compatibility.
    Argon2 hashes start with '$argon2', bcrypt hashes start with '$2'.

    Args:
        plain_password: The plaintext password to verify
        hashed_password: The hashed password to check against

    Returns:
        True if password matches, False otherwise
    """
    # Try Argon2 first (new hashes)
    if hashed_password.startswith("$argon2"):
        return password_hasher.verify(plain_password, hashed_password)

    # Fallback to bcrypt for legacy hashes
    if hashed_password.startswith("$2"):
        return _legacy_pwd_context.verify(plain_password, hashed_password)

    # Unknown hash format
    return False


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2 (ARCH-11).

    Args:
        password: The plaintext password to hash

    Returns:
        Argon2 hashed password string
    """
    return password_hasher.hash(password)


def needs_rehash(hashed_password: str) -> bool:
    """Check if a password hash should be upgraded to Argon2.

    Used during login to migrate legacy bcrypt hashes to Argon2.

    Args:
        hashed_password: The current password hash

    Returns:
        True if hash should be upgraded, False otherwise
    """
    # Legacy bcrypt hashes should be upgraded
    if hashed_password.startswith("$2"):
        return True

    # For Argon2 hashes, no rehash needed (pwdlib doesn't expose rehash check,
    # but recommended() always uses current best parameters)
    return False
