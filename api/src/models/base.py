"""
Base ORM model with common fields: UUID, timestamps, soft delete
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

# Base class for all models
Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model with common fields for all entities.
    
    Fields:
    - id: UUID primary key
    - created_at: Creation timestamp
    - updated_at: Last update timestamp
    - deleted_at: Soft delete timestamp (NULL = not deleted)
    """

    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def is_deleted(self) -> bool:
        """Check if entity is soft-deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark entity as deleted without removing from database."""
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        """Restore a soft-deleted entity."""
        self.deleted_at = None
