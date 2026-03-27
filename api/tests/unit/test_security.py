"""
Unit tests for security utilities
"""
import pytest
from datetime import timedelta
from shared.src.security import (
    hash_password,
    verify_password,
    generate_random_secret,
    JWTHandler,
)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        assert hashed != password
        assert len(hashed) > 20

    def test_verify_password(self):
        """Test password verification."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        assert verify_password(password, hashed)

    def test_verify_wrong_password(self):
        """Test verification fails with wrong password."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        assert not verify_password("WrongPassword", hashed)


class TestRandomSecret:
    """Test random secret generation."""

    def test_generate_random_secret(self):
        """Test generating random secrets."""
        secret = generate_random_secret()
        assert isinstance(secret, str)
        assert len(secret) > 20

    def test_generate_different_secrets(self):
        """Test that generated secrets are unique."""
        secret1 = generate_random_secret()
        secret2 = generate_random_secret()
        assert secret1 != secret2


class TestJWTHandler:
    """Test JWT token creation and validation."""

    @pytest.fixture
    def jwt_handler(self):
        """Create JWT handler instance."""
        return JWTHandler(
            secret_key="test-secret-key-very-long",
            algorithm="HS256",
            access_token_expire_minutes=15,
            refresh_token_expire_days=7,
        )

    def test_create_access_token(self, jwt_handler):
        """Test creating an access token."""
        data = {"sub": "user123", "email": "test@example.com"}
        token = jwt_handler.create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 20

    def test_create_refresh_token(self, jwt_handler):
        """Test creating a refresh token."""
        data = {"sub": "user123"}
        token = jwt_handler.create_refresh_token(data)
        assert isinstance(token, str)
        assert len(token) > 20

    def test_decode_token(self, jwt_handler):
        """Test decoding a token."""
        data = {"sub": "user123", "email": "test@example.com"}
        token = jwt_handler.create_access_token(data)
        decoded = jwt_handler.decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "test@example.com"

    def test_decode_invalid_token(self, jwt_handler):
        """Test decoding an invalid token."""
        decoded = jwt_handler.decode_token("invalid.token.here")
        assert decoded is None

    def test_verify_token_type(self, jwt_handler):
        """Test token type verification."""
        data = {"sub": "user123"}
        access_token = jwt_handler.create_access_token(data)
        refresh_token = jwt_handler.create_refresh_token(data)

        assert jwt_handler.verify_token_type(access_token, "access")
        assert not jwt_handler.verify_token_type(access_token, "refresh")
        assert jwt_handler.verify_token_type(refresh_token, "refresh")
        assert not jwt_handler.verify_token_type(refresh_token, "access")

    def test_token_expiration(self, jwt_handler):
        """Test that expired tokens are not valid."""
        data = {"sub": "user123"}
        # Create token that expires immediately
        token = jwt_handler.create_access_token(
            data, expires_delta=timedelta(seconds=-1)
        )
        decoded = jwt_handler.decode_token(token)
        assert decoded is None
