"""
Tests for user management endpoints
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from src.main import app
from shared.src.enums import UserRole

client = TestClient(app)


@pytest.mark.asyncio
async def test_create_user_success():
    """Test successful user creation."""
    response = client.post(
        "/api/v1/users",
        json={
            "email": f"newuser{uuid4()}@example.com",
            "password": "SecurePassword123!",
            "role": "USER",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] is not None
    assert data["role"] == "USER"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_user_duplicate_email(db_with_user, test_user_data):
    """Test create user with duplicate email."""
    response = client.post(
        "/api/v1/users",
        json={
            "email": test_user_data["email"],
            "password": "AnotherPassword123!",
            "role": "USER",
        },
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_user_weak_password():
    """Test create user with weak password."""
    response = client.post(
        "/api/v1/users",
        json={
            "email": f"user{uuid4()}@example.com",
            "password": "weak",
            "role": "USER",
        },
    )
    assert response.status_code == 400
    assert "at least 8 characters" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_success(db_with_user, test_user):
    """Test get user by ID."""
    response = client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert str(data["id"]) == str(test_user.id)
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_get_user_not_found():
    """Test get non-existent user."""
    response = client.get(f"/api/v1/users/{uuid4()}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_users(db_with_user, test_user):
    """Test list users."""
    response = client.get("/api/v1/users?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert data["skip"] == 0
    assert data["limit"] == 10
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_update_user_success(db_with_user, test_user):
    """Test update user."""
    new_email = f"updated{uuid4()}@example.com"
    response = client.patch(
        f"/api/v1/users/{test_user.id}",
        json={"email": new_email, "role": "ADMIN"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == new_email
    assert data["role"] == "ADMIN"


@pytest.mark.asyncio
async def test_update_user_not_found():
    """Test update non-existent user."""
    response = client.patch(
        f"/api/v1/users/{uuid4()}",
        json={"email": "newemail@example.com"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deactivate_user(db_with_user, test_user):
    """Test deactivate user."""
    response = client.patch(f"/api/v1/users/{test_user.id}/deactivate")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_delete_user(db_with_user, test_user):
    """Test delete user."""
    response = client.delete(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

    # Verify user is gone
    response = client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 404
