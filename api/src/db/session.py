"""
SQLAlchemy async session factory and utilities
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager

from src.config import settings
from src.models.base import Base


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    future=True,
    pool_pre_ping=True,
    poolclass=NullPool,  # Disable connection pooling for now (can be changed for production)
)

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for database session.
    Usage in FastAPI: 
        @app.get("/")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """
    Context manager for database session.
    Usage:
        async with get_db_context() as session:
            ...
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Initialize database (create tables).
    Call this at startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """
    Drop all tables from database.
    WARNING: This is destructive!
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_db():
    """
    Close database connection.
    Call this at shutdown.
    """
    await engine.dispose()
