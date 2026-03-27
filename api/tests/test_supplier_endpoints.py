"""
Tests for supplier endpoints
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from src.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_create_supplier_success():
    """Test successful supplier creation."""
    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": f"Supplier {uuid4().hex[:8]}",
            "fiscal_code": f"FS{uuid4().hex[:8].upper()}",
            "address": "456 Tech Drive",
            "city": "Milan",
            "country": "Italy",
            "phone": "+39-02-5555555",
            "email": "sales@supplier.it",
            "contact_person": "Maria Bianchi",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] is not None
    assert data["fiscal_code"] is not None


@pytest.mark.asyncio
async def test_create_supplier_duplicate_fiscal_code():
    """Test create supplier with duplicate fiscal code."""
    fiscal_code = f"FS{uuid4().hex[:8].upper()}"
    
    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Supplier One",
            "fiscal_code": fiscal_code,
            "address": "456 Tech Drive",
            "city": "Milan",
            "country": "Italy",
        },
    )
    assert response.status_code == 201
    
    # Second with same code fails
    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Supplier Two",
            "fiscal_code": fiscal_code,
            "address": "789 Another St",
            "city": "Rome",
            "country": "Italy",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_suppliers():
    """Test list suppliers."""
    response = client.get("/api/v1/suppliers?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "suppliers" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_supplier_success():
    """Test get supplier by ID."""
    create_response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Test Supplier",
            "fiscal_code": f"FS{uuid4().hex[:8].upper()}",
            "address": "456 Tech Drive",
            "city": "Milan",
            "country": "Italy",
        },
    )
    supplier_id = create_response.json()["id"]
    
    response = client.get(f"/api/v1/suppliers/{supplier_id}")
    assert response.status_code == 200
    data = response.json()
    assert str(data["id"]) == str(supplier_id)


@pytest.mark.asyncio
async def test_update_supplier():
    """Test update supplier."""
    create_response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Original Supplier",
            "fiscal_code": f"FS{uuid4().hex[:8].upper()}",
            "address": "456 Tech Drive",
            "city": "Milan",
            "country": "Italy",
        },
    )
    supplier_id = create_response.json()["id"]
    
    response = client.patch(
        f"/api/v1/suppliers/{supplier_id}",
        json={"name": "Updated Supplier", "city": "Rome"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Supplier"
    assert data["city"] == "Rome"


@pytest.mark.asyncio
async def test_delete_supplier():
    """Test delete supplier."""
    create_response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Supplier to Delete",
            "fiscal_code": f"FS{uuid4().hex[:8].upper()}",
            "address": "456 Tech Drive",
            "city": "Milan",
            "country": "Italy",
        },
    )
    supplier_id = create_response.json()["id"]
    
    response = client.delete(f"/api/v1/suppliers/{supplier_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
