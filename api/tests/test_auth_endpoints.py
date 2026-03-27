"""
Tests for authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.services.auth import AuthService
from shared.src.exceptions import AuthException


client = TestClient(app)


@pytest.mark.asyncio
async def test_login_success(db_with_user, test_user_data):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_invalid_email():
    """Test login with invalid email."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_invalid_password(db_with_user, test_user_data):
    """Test login with invalid password."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_token_success(db_with_user, test_user_data):
    """Test successful token refresh."""
    # First, get tokens from login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    login_data = login_response.json()
    refresh_token = login_data["refresh_token"]

    # Now refresh
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_invalid():
    """Test refresh with invalid token."""
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid-token"},
    )
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


@pytest.mark.asyncio
async def test_logout():
    """Test logout endpoint."""
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"
