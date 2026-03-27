"""
Contract service - CRUD operations and business logic
"""
from uuid import UUID
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from src.models.contract import Contract
from src.models.client import Client
from src.models.supplier import Supplier
from shared.src.exceptions import NotFoundException, ConflictException, ValidationException
from shared.src.enums import ContractStatus, ContractType


class ContractService:
    """Service for contract management."""

    async def create_contract(
        self,
        db: AsyncSession,
        client_id: UUID,
        supplier_id: UUID,
        contract_number: str,
        title: str,
        amount: float,
        contract_type: ContractType,
        start_date: datetime,
        end_date: datetime,
        description: Optional[str] = None,
        client_signatory_id: Optional[UUID] = None,
        supplier_signatory_id: Optional[UUID] = None,
    ) -> Contract:
        """
        Create a new contract.
        
        Args:
            db: Database session
            client_id: Client ID
            supplier_id: Supplier ID
            contract_number: Unique contract identifier
            title: Contract title
            amount: Contract amount
            contract_type: Type of contract
            start_date: Start date
            end_date: End date
            description: Contract description (optional)
            client_signatory_id: Authorized client signer (optional)
            supplier_signatory_id: Authorized supplier signer (optional)
            
        Returns:
            Created contract
            
        Raises:
            ConflictException: If contract_number already exists
            ValidationException: If validation fails
            NotFoundException: If client/supplier not found
        """
        # Validate contract_number is unique
        stmt = select(Contract).where(Contract.contract_number == contract_number).where(Contract.deleted_at.is_(None))
        result = await db.execute(stmt)
        if result.scalars().first():
            raise ConflictException("Contract", f"contract_number {contract_number} already exists")

        # Validate client exists
        client_stmt = select(Client).where(Client.id == client_id).where(Client.deleted_at.is_(None))
        client_result = await db.execute(client_stmt)
        if not client_result.scalars().first():
            raise NotFoundException("Client", str(client_id))

        # Validate supplier exists
        supplier_stmt = select(Supplier).where(Supplier.id == supplier_id).where(Supplier.deleted_at.is_(None))
        supplier_result = await db.execute(supplier_stmt)
        if not supplier_result.scalars().first():
            raise NotFoundException("Supplier", str(supplier_id))

        # Validate dates
        if end_date <= start_date:
            raise ValidationException("End date must be after start date")

        # Validate amount
        if amount <= 0:
            raise ValidationException("Contract amount must be greater than 0")

        # Validate required fields
        if not title or len(title.strip()) == 0:
            raise ValidationException("Contract title is required")

        # Create contract
        contract = Contract(
            client_id=client_id,
            supplier_id=supplier_id,
            contract_number=contract_number,
            title=title,
            amount=amount,
            contract_type=contract_type,
            start_date=start_date,
            end_date=end_date,
            status=ContractStatus.DRAFT,
            description=description,
            client_signatory_id=client_signatory_id,
            supplier_signatory_id=supplier_signatory_id,
        )
        db.add(contract)
        await db.commit()
        await db.refresh(contract)

        return contract

    async def get_contract_by_id(self, db: AsyncSession, contract_id: UUID) -> Contract:
        """Get contract by ID."""
        stmt = select(Contract).where(Contract.id == contract_id).where(Contract.deleted_at.is_(None))
        result = await db.execute(stmt)
        contract = result.scalars().first()

        if not contract:
            raise NotFoundException("Contract", str(contract_id))

        return contract

    async def get_contract_by_number(self, db: AsyncSession, contract_number: str) -> Optional[Contract]:
        """Get contract by contract number."""
        stmt = select(Contract).where(Contract.contract_number == contract_number).where(Contract.deleted_at.is_(None))
        result = await db.execute(stmt)
        return result.scalars().first()

    async def list_contracts(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ContractStatus] = None,
        client_id: Optional[UUID] = None,
        supplier_id: Optional[UUID] = None,
    ) -> tuple[List[Contract], int]:
        """List contracts with pagination and optional filtering."""
        base_stmt = select(Contract).where(Contract.deleted_at.is_(None))
        
        if status:
            base_stmt = base_stmt.where(Contract.status == status)
        if client_id:
            base_stmt = base_stmt.where(Contract.client_id == client_id)
        if supplier_id:
            base_stmt = base_stmt.where(Contract.supplier_id == supplier_id)

        # Get total count
        count_stmt = select(func.count(Contract.id)).select_from(Contract).where(Contract.deleted_at.is_(None))
        if status:
            count_stmt = count_stmt.where(Contract.status == status)
        if client_id:
            count_stmt = count_stmt.where(Contract.client_id == client_id)
        if supplier_id:
            count_stmt = count_stmt.where(Contract.supplier_id == supplier_id)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = base_stmt.offset(skip).limit(limit).order_by(Contract.created_at.desc())
        result = await db.execute(stmt)
        contracts = result.scalars().all()

        return contracts, total

    async def get_expiring_contracts(
        self,
        db: AsyncSession,
        days: int = 30,
    ) -> List[Contract]:
        """Get contracts expiring within N days."""
        today = datetime.utcnow().date()
        expiry_date = today + timedelta(days=days)
        
        stmt = (
            select(Contract)
            .where(Contract.deleted_at.is_(None))
            .where(Contract.status != ContractStatus.EXPIRED)
            .where(Contract.status != ContractStatus.CANCELLED)
            .where(Contract.end_date >= today)
            .where(Contract.end_date <= expiry_date)
            .order_by(Contract.end_date)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def update_contract(
        self,
        db: AsyncSession,
        contract_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        amount: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        client_signatory_id: Optional[UUID] = None,
        supplier_signatory_id: Optional[UUID] = None,
    ) -> Contract:
        """Update contract details."""
        contract = await self.get_contract_by_id(db, contract_id)

        if title is not None:
            contract.title = title
        if description is not None:
            contract.description = description
        if amount is not None:
            if amount <= 0:
                raise ValidationException("Contract amount must be greater than 0")
            contract.amount = amount
        if start_date is not None:
            contract.start_date = start_date
        if end_date is not None:
            if start_date and end_date <= start_date:
                raise ValidationException("End date must be after start date")
            contract.end_date = end_date
        if client_signatory_id is not None:
            contract.client_signatory_id = client_signatory_id
        if supplier_signatory_id is not None:
            contract.supplier_signatory_id = supplier_signatory_id

        db.add(contract)
        await db.commit()
        await db.refresh(contract)

        return contract

    async def change_status(
        self,
        db: AsyncSession,
        contract_id: UUID,
        new_status: ContractStatus,
    ) -> Contract:
        """Change contract status."""
        contract = await self.get_contract_by_id(db, contract_id)

        # Validate status transition
        if contract.status == ContractStatus.CANCELLED:
            raise ValidationException("Cannot change status of a cancelled contract")

        contract.status = new_status
        db.add(contract)
        await db.commit()
        await db.refresh(contract)

        return contract

    async def deactivate_contract(self, db: AsyncSession, contract_id: UUID) -> Contract:
        """Deactivate a contract (soft delete)."""
        contract = await self.get_contract_by_id(db, contract_id)
        contract.deleted_at = func.now()
        db.add(contract)
        await db.commit()
        await db.refresh(contract)

        return contract

    async def delete_contract(self, db: AsyncSession, contract_id: UUID) -> None:
        """Delete a contract permanently."""
        contract = await self.get_contract_by_id(db, contract_id)
        await db.delete(contract)
        await db.commit()
