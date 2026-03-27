"""
Supplement service - Contract amendments and modifications
"""
from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.models.supplement import Supplement
from src.models.contract import Contract
from shared.src.exceptions import NotFoundException, ValidationException
from shared.src.enums import SupplementStatus


class SupplementService:
    """Service for supplement (amendment) management."""

    async def create_supplement(
        self,
        db: AsyncSession,
        contract_id: UUID,
        title: str,
        description: Optional[str] = None,
        modifications_detail: Optional[dict] = None,
    ) -> Supplement:
        """
        Create a new supplement (contract amendment).
        
        Args:
            db: Database session
            contract_id: Contract ID
            title: Amendment title
            description: Amendment description (optional)
            modifications_detail: JSON object with modification details (optional)
            
        Returns:
            Created supplement
            
        Raises:
            NotFoundException: If contract not found
            ValidationException: If validation fails
        """
        # Validate contract exists
        contract_stmt = select(Contract).where(Contract.id == contract_id).where(Contract.deleted_at.is_(None))
        contract_result = await db.execute(contract_stmt)
        if not contract_result.scalars().first():
            raise NotFoundException("Contract", str(contract_id))

        # Validate required fields
        if not title or len(title.strip()) == 0:
            raise ValidationException("Supplement title is required")

        # Create supplement
        supplement = Supplement(
            contract_id=contract_id,
            title=title,
            description=description,
            modifications_detail=modifications_detail or {},
            status=SupplementStatus.DRAFT,
        )
        db.add(supplement)
        await db.commit()
        await db.refresh(supplement)

        return supplement

    async def get_supplement_by_id(self, db: AsyncSession, supplement_id: UUID) -> Supplement:
        """Get supplement by ID."""
        stmt = select(Supplement).where(Supplement.id == supplement_id).where(Supplement.deleted_at.is_(None))
        result = await db.execute(stmt)
        supplement = result.scalars().first()

        if not supplement:
            raise NotFoundException("Supplement", str(supplement_id))

        return supplement

    async def list_supplements_by_contract(
        self,
        db: AsyncSession,
        contract_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[SupplementStatus] = None,
    ) -> tuple[List[Supplement], int]:
        """List supplements for a specific contract."""
        base_stmt = select(Supplement).where(Supplement.contract_id == contract_id).where(Supplement.deleted_at.is_(None))
        
        if status:
            base_stmt = base_stmt.where(Supplement.status == status)

        # Get total count
        count_stmt = select(func.count(Supplement.id)).select_from(Supplement).where(Supplement.contract_id == contract_id).where(Supplement.deleted_at.is_(None))
        if status:
            count_stmt = count_stmt.where(Supplement.status == status)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = base_stmt.offset(skip).limit(limit).order_by(Supplement.created_at.desc())
        result = await db.execute(stmt)
        supplements = result.scalars().all()

        return supplements, total

    async def update_supplement(
        self,
        db: AsyncSession,
        supplement_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        modifications_detail: Optional[dict] = None,
    ) -> Supplement:
        """Update supplement details."""
        supplement = await self.get_supplement_by_id(db, supplement_id)

        if title is not None:
            if len(title.strip()) == 0:
                raise ValidationException("Supplement title cannot be empty")
            supplement.title = title
        if description is not None:
            supplement.description = description
        if modifications_detail is not None:
            supplement.modifications_detail = modifications_detail

        db.add(supplement)
        await db.commit()
        await db.refresh(supplement)

        return supplement

    async def change_status(
        self,
        db: AsyncSession,
        supplement_id: UUID,
        new_status: SupplementStatus,
    ) -> Supplement:
        """Change supplement status."""
        supplement = await self.get_supplement_by_id(db, supplement_id)
        supplement.status = new_status
        db.add(supplement)
        await db.commit()
        await db.refresh(supplement)

        return supplement

    async def deactivate_supplement(self, db: AsyncSession, supplement_id: UUID) -> Supplement:
        """Deactivate a supplement (soft delete)."""
        supplement = await self.get_supplement_by_id(db, supplement_id)
        supplement.deleted_at = func.now()
        db.add(supplement)
        await db.commit()
        await db.refresh(supplement)

        return supplement

    async def delete_supplement(self, db: AsyncSession, supplement_id: UUID) -> None:
        """Delete a supplement permanently."""
        supplement = await self.get_supplement_by_id(db, supplement_id)
        await db.delete(supplement)
        await db.commit()
