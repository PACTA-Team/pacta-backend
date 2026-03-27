"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "role": "editor",
    }


@pytest.fixture
def test_client_data():
    """Sample client data for testing."""
    return {
        "name": "Test Client Corp",
        "address": "123 Main St",
        "city": "New York",
        "country": "USA",
        "fiscal_code": "12345678",
        "phone": "+1-555-0100",
        "email": "client@example.com",
        "contact_person": "John Doe",
    }


@pytest.fixture
def test_supplier_data():
    """Sample supplier data for testing."""
    return {
        "name": "Test Supplier Inc",
        "address": "456 Oak Ave",
        "city": "Los Angeles",
        "country": "USA",
        "fiscal_code": "87654321",
        "phone": "+1-555-0200",
        "email": "supplier@example.com",
        "contact_person": "Jane Smith",
    }


@pytest.fixture
def test_contract_data():
    """Sample contract data for testing."""
    return {
        "contract_number": "CNT-2026-001",
        "title": "Test Contract",
        "description": "A test contract for unit testing",
        "amount": 10000.00,
        "contract_type": "service",
        "status": "draft",
    }
