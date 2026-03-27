"""
Tests for client endpoints
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from src.main import app
from src.services.client import ClientService

client = TestClient(app)


@pytest.mark.asyncio
async def test_create_client_success(db_session):
    """Test successful client creation."""
    response = client.post(
        "/api/v1/clients",
        json={
            "name": f"Client {uuid4().hex[:8]}",
            "fiscal_code": f"FC{uuid4().hex[:8].upper()}",
            "address": "123 Business St",
            "city": "Rome",
            "country": "Italy",
            "phone": "+39-06-1234567",
            "email": "contact@client.it",
            "contact_person": "John Rossi",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] is not None
    assert data["fiscal_code"] is not None


@pytest.mark.asyncio
async def test_create_client_duplicate_fiscal_code(db_with_client):
    """Test create client with duplicate fiscal code."""
    response = client.post(
        "/api/v1/clients",
        json={
            "name": "Another Client",
            "fiscal_code": "EXISTING123",
            "address": "123 Business St",
            "city": "Rome",
            "country": "Italy",
        },
    )
    # First creation succeeds
    assert response.status_code == 201
    
    # Second with same code fails
    response = client.post(
        "/api/v1/clients",
        json={
            "name": "Another Client",
            "fiscal_code": "EXISTING123",
            "address": "456 Different St",
            "city": "Milan",
            "country": "Italy",
        },
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_client_missing_required_fields():
    """Test create client with missing required fields."""
    response = client.post(
        "/api/v1/clients",
        json={
            "fiscal_code": "FC123456",
            "address": "123 Business St",
            "city": "Rome",
            "country": "Italy",
        },
    )
    assert response.status_code == 400
    assert "name" in str(response.json()).lower() or "required" in str(response.json()).lower()


@pytest.mark.asyncio
async def test_list_clients(db_with_client):
    """Test list clients."""
    response = client.get("/api/v1/clients?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "clients" in data
    assert "total" in data
    assert data["skip"] == 0
    assert data["limit"] == 10


@pytest.mark.asyncio
async def test_list_clients_with_country_filter(db_with_client):
    """Test list clients with country filter."""
    response = client.get("/api/v1/clients?skip=0&limit=10&country=Italy")
    assert response.status_code == 200
    data = response.json()
    assert "clients" in data


@pytest.mark.asyncio
async def test_get_client_success(db_with_client):
    """Test get client by ID."""
    # First create a client to get its ID
    create_response = client.post(
        "/api/v1/clients",
        json={
            "name": "Test Client",
            "fiscal_code": f"FC{uuid4().hex[:8].upper()}",
            "address": "123 Business St",
            "city": "Rome",
            "country": "Italy",
        },
    )
    client_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/api/v1/clients/{client_id}")
    assert response.status_code == 200
    data = response.json()
    assert str(data["id"]) == str(client_id)


@pytest.mark.asyncio
async def test_update_client(db_with_client):
    """Test update client."""
    # Create a client first
    create_response = client.post(
        "/api/v1/clients",
        json={
            "name": "Original Name",
            "fiscal_code": f"FC{uuid4().hex[:8].upper()}",
            "address": "123 Business St",
            "city": "Rome",
            "country": "Italy",
        },
    )
    client_id = create_response.json()["id"]
    
    # Update it
    response = client.patch(
        f"/api/v1/clients/{client_id}",
        json={"name": "Updated Name", "city": "Milan"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["city"] == "Milan"


@pytest.mark.asyncio
async def test_delete_client(db_with_client):
    """Test delete client."""
    # Create a client first
    create_response = client.post(
        "/api/v1/clients",
        json={
            "name": "Client to Delete",
            "fiscal_code": f"FC{uuid4().hex[:8].upper()}",
            "address": "123 Business St",
            "city": "Rome",
            "country": "Italy",
        },
    )
    client_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/v1/clients/{client_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
