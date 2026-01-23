"""Tests for password hashing and security utilities.

Verifies ARCH-11 compliance: Argon2 password hashing via pwdlib.
Verifies ARCH-12 compliance: Token type validation.
"""

from datetime import timedelta

import pytest
from passlib.context import CryptContext

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    needs_rehash,
    verify_password,
)


class TestPasswordHashing:
    """Tests for Argon2 password hashing (ARCH-11)."""

    def test_get_password_hash_returns_argon2_hash(self) -> None:
        """Verify that new hashes use Argon2 algorithm."""
        password = "SecurePassword123"
        hashed = get_password_hash(password)

        # Argon2 hashes start with $argon2
        assert hashed.startswith("$argon2")

    def test_get_password_hash_different_for_same_password(self) -> None:
        """Verify that hashing the same password twice produces different hashes (salt)."""
        password = "SecurePassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2

    def test_verify_password_with_argon2_hash(self) -> None:
        """Verify password verification works with Argon2 hashes."""
        password = "SecurePassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False

    def test_verify_password_with_empty_password(self) -> None:
        """Verify empty password handling."""
        hashed = get_password_hash("SomePassword")

        assert verify_password("", hashed) is False


class TestBackwardCompatibility:
    """Tests for backward compatibility with bcrypt hashes."""

    @pytest.fixture
    def bcrypt_context(self) -> CryptContext:
        """Create a bcrypt context for generating legacy hashes."""
        return CryptContext(schemes=["bcrypt"], deprecated="auto")

    def test_verify_password_with_bcrypt_hash(
        self, bcrypt_context: CryptContext
    ) -> None:
        """Verify password verification works with legacy bcrypt hashes."""
        password = "LegacyPassword123"
        bcrypt_hash = bcrypt_context.hash(password)

        # Bcrypt hashes start with $2
        assert bcrypt_hash.startswith("$2")

        # Should still verify correctly
        assert verify_password(password, bcrypt_hash) is True
        assert verify_password("WrongPassword", bcrypt_hash) is False

    def test_needs_rehash_for_bcrypt(self, bcrypt_context: CryptContext) -> None:
        """Verify that bcrypt hashes are flagged for rehash."""
        password = "LegacyPassword123"
        bcrypt_hash = bcrypt_context.hash(password)

        assert needs_rehash(bcrypt_hash) is True

    def test_needs_rehash_for_argon2(self) -> None:
        """Verify that fresh Argon2 hashes don't need rehash."""
        password = "NewPassword123"
        argon2_hash = get_password_hash(password)

        assert needs_rehash(argon2_hash) is False

    def test_verify_password_with_unknown_hash_format(self) -> None:
        """Verify that unknown hash formats return False."""
        password = "SomePassword"
        invalid_hash = "not_a_valid_hash"

        assert verify_password(password, invalid_hash) is False


class TestPasswordStrength:
    """Tests for password hashing with various inputs."""

    def test_hash_and_verify_unicode_password(self) -> None:
        """Verify Unicode passwords work correctly."""
        password = "Пароль123"  # Russian characters
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_hash_and_verify_long_password(self) -> None:
        """Verify long passwords work correctly."""
        password = "A" * 256  # Very long password
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_hash_and_verify_special_characters(self) -> None:
        """Verify passwords with special characters work."""
        password = "P@$$w0rd!#%^&*()_+-=[]{}|;':\",./<>?"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True


class TestTokenTypes:
    """Tests for JWT token type claims (ARCH-12)."""

    def test_access_token_has_access_type(self) -> None:
        """Verify access tokens include type='access' claim."""
        import jwt

        from app.core.config import settings
        from app.core.security import ALGORITHM

        token = create_access_token(
            subject="test-user-id", expires_delta=timedelta(hours=1)
        )
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["type"] == "access"
        assert payload["sub"] == "test-user-id"

    def test_refresh_token_has_refresh_type(self) -> None:
        """Verify refresh tokens include type='refresh' claim."""
        import jwt

        from app.core.config import settings
        from app.core.security import ALGORITHM

        token = create_refresh_token(
            subject="test-user-id", expires_delta=timedelta(days=7)
        )
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["type"] == "refresh"
        assert payload["sub"] == "test-user-id"

    def test_access_and_refresh_tokens_are_different(self) -> None:
        """Verify access and refresh tokens have different type claims."""
        import jwt

        from app.core.config import settings
        from app.core.security import ALGORITHM

        access_token = create_access_token(
            subject="test-user-id", expires_delta=timedelta(hours=1)
        )
        refresh_token = create_refresh_token(
            subject="test-user-id", expires_delta=timedelta(days=7)
        )

        access_payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        refresh_payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )

        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"
        assert access_payload["type"] != refresh_payload["type"]
