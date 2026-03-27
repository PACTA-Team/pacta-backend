"""
Signatory service - CRUD operations and business logic
"""
from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.models.signatory import Signatory
from shared.src.exceptions import NotFoundException, ConflictException, ValidationException
from shared.src.enums import IdentityType


class SignatoryService:
    """Service for signatory management."""

    async def create_signatory(
        self,
        db: AsyncSession,
        entity_type: IdentityType,
        entity_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        phone: Optional[str] = None,
        position: Optional[str] = None,
        identity_document: Optional[str] = None,
    ) -> Signatory:
        """
        Create a new signatory.
        
        Args:
            db: Database session
            entity_type: Type of entity (CLIENT or SUPPLIER)
            entity_id: ID of the client or supplier
            first_name: First name
            last_name: Last name
            email: Email address
            phone: Phone number (optional)
            position: Job position (optional)
            identity_document: ID number/document (optional)
            
        Returns:
            Created signatory
            
        Raises:
            ConflictException: If email already exists for this entity
            ValidationException: If required fields invalid
        """
        # Validate required fields
        if not first_name or len(first_name.strip()) == 0:
            raise ValidationException("First name is required")
        if not last_name or len(last_name.strip()) == 0:
            raise ValidationException("Last name is required")
        if not email or len(email.strip()) == 0:
            raise ValidationException("Email is required")

        # Check if email already exists for this entity
        stmt = (
            select(Signatory)
            .where(Signatory.entity_type == entity_type)
            .where(Signatory.entity_id == entity_id)
            .where(Signatory.email == email)
            .where(Signatory.deleted_at.is_(None))
        )
        result = await db.execute(stmt)
        if result.scalars().first():
            raise ConflictException("Signatory", f"email {email} already exists for this entity")

        # Create signatory
        signatory = Signatory(
            entity_type=entity_type,
            entity_id=entity_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            position=position,
            identity_document=identity_document,
            is_active=True,
        )
        db.add(signatory)
        await db.commit()
        await db.refresh(signatory)

        return signatory

    async def get_signatory_by_id(self, db: AsyncSession, signatory_id: UUID) -> Signatory:
        """Get signatory by ID."""
        stmt = select(Signatory).where(Signatory.id == signatory_id).where(Signatory.deleted_at.is_(None))
        result = await db.execute(stmt)
        signatory = result.scalars().first()

        if not signatory:
            raise NotFoundException("Signatory", str(signatory_id))

        return signatory

    async def list_signatories_by_entity(
        self,
        db: AsyncSession,
        entity_type: IdentityType,
        entity_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Signatory], int]:
        """List signatories for a specific entity (client/supplier)."""
        base_stmt = (
            select(Signatory)
            .where(Signatory.entity_type == entity_type)
            .where(Signatory.entity_id == entity_id)
            .where(Signatory.deleted_at.is_(None))
        )

        count_stmt = (
            select(func.count(Signatory.id))
            .select_from(Signatory)
            .where(Signatory.entity_type == entity_type)
            .where(Signatory.entity_id == entity_id)
            .where(Signatory.deleted_at.is_(None))
        )
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = base_stmt.offset(skip).limit(limit).order_by(Signatory.created_at.desc())
        result = await db.execute(stmt)
        signatories = result.scalars().all()

        return signatories, total

    async def update_signatory(
        self,
        db: AsyncSession,
        signatory_id: UUID,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        position: Optional[str] = None,
        identity_document: Optional[str] = None,
    ) -> Signatory:
        """Update signatory details."""
        signatory = await self.get_signatory_by_id(db, signatory_id)

        if first_name is not None:
            signatory.first_name = first_name
        if last_name is not None:
            signatory.last_name = last_name
        if email is not None:
            signatory.email = email
        if phone is not None:
            signatory.phone = phone
        if position is not None:
            signatory.position = position
        if identity_document is not None:
            signatory.identity_document = identity_document

        db.add(signatory)
        await db.commit()
        await db.refresh(signatory)

        return signatory

    async def deactivate_signatory(self, db: AsyncSession, signatory_id: UUID) -> Signatory:
        """Deactivate a signatory (soft delete)."""
        signatory = await self.get_signatory_by_id(db, signatory_id)
        signatory.deleted_at = func.now()
        signatory.is_active = False
        db.add(signatory)
        await db.commit()
        await db.refresh(signatory)

        return signatory

    async def delete_signatory(self, db: AsyncSession, signatory_id: UUID) -> None:
        """Delete a signatory permanently."""
        signatory = await self.get_signatory_by_id(db, signatory_id)
        await db.delete(signatory)
        await db.commit()
