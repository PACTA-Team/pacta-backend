"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.models.base import Base
from src.models.user import User
from src.models.client import Client
from src.models.supplier import Supplier
from src.models.contract import Contract
from src.config import settings
from shared.src.enums import UserRole, ContractType, ContractStatus
from shared.src.security import hash_password


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    async_session = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": f"test{uuid4()}@example.com",
        "password": "TestPassword123!",
        "role": UserRole.USER,
    }


@pytest.fixture
async def db_with_user(db_session, test_user_data):
    """Create a test user in the database."""
    user = User(
        email=test_user_data["email"],
        password_hash=hash_password(test_user_data["password"]),
        role=test_user_data["role"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return db_session


@pytest.fixture
async def test_user(db_session, test_user_data):
    """Get the test user from database."""
    from sqlalchemy import select
    
    stmt = select(User).where(User.email == test_user_data["email"])
    result = await db_session.execute(stmt)
    return result.scalars().first()


@pytest.fixture
def test_client_data():
    """Sample client data for testing."""
    return {
        "name": f"Test Client {uuid4().hex[:8]}",
        "address": "123 Main St",
        "city": "New York",
        "country": "USA",
        "fiscal_code": f"FC{uuid4().hex[:8].upper()}",
        "phone": "+1-555-0100",
        "email": f"client{uuid4()}@example.com",
        "contact_person": "John Doe",
    }


@pytest.fixture
async def db_with_client(db_session, test_client_data):
    """Create a test client in the database."""
    client = Client(**test_client_data)
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    return db_session


@pytest.fixture
def test_supplier_data():
    """Sample supplier data for testing."""
    return {
        "name": f"Test Supplier {uuid4().hex[:8]}",
        "address": "456 Oak Ave",
        "city": "Los Angeles",
        "country": "USA",
        "fiscal_code": f"FS{uuid4().hex[:8].upper()}",
        "phone": "+1-555-0200",
        "email": f"supplier{uuid4()}@example.com",
        "contact_person": "Jane Smith",
    }


@pytest.fixture
async def db_with_supplier(db_session, test_supplier_data):
    """Create a test supplier in the database."""
    supplier = Supplier(**test_supplier_data)
    db_session.add(supplier)
    await db_session.commit()
    await db_session.refresh(supplier)
    return db_session


@pytest.fixture
def test_contract_data(db_with_client, test_client_data, test_supplier_data):
    """Sample contract data for testing."""
    return {
        "contract_number": f"CNT-{uuid4().hex[:8].upper()}",
        "title": "Test Contract",
        "description": "A test contract for unit testing",
        "amount": 10000.00,
        "contract_type": ContractType.SERVICE,
        "status": ContractStatus.DRAFT,
    }


@pytest.fixture
async def db_with_contract(db_session, db_with_client, db_with_supplier, test_contract_data):
    """Create a test contract in the database."""
    from sqlalchemy import select
    
    # Get the created client and supplier
    client_stmt = select(Client).order_by(Client.created_at.desc()).limit(1)
    client_result = await db_session.execute(client_stmt)
    client = client_result.scalars().first()
    
    supplier_stmt = select(Supplier).order_by(Supplier.created_at.desc()).limit(1)
    supplier_result = await db_session.execute(supplier_stmt)
    supplier = supplier_result.scalars().first()
    
    contract = Contract(
        client_id=client.id,
        supplier_id=supplier.id,
        **test_contract_data
    )
    db_session.add(contract)
    await db_session.commit()
    await db_session.refresh(contract)
    return db_session

