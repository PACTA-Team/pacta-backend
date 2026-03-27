"""
Supplier service - CRUD operations and business logic
"""
from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.models.supplier import Supplier
from shared.src.exceptions import NotFoundException, ConflictException, ValidationException


class SupplierService:
    """Service for supplier management."""

    async def create_supplier(
        self,
        db: AsyncSession,
        name: str,
        fiscal_code: str,
        address: str,
        city: str,
        country: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        contact_person: Optional[str] = None,
    ) -> Supplier:
        """
        Create a new supplier.
        
        Args:
            db: Database session
            name: Supplier name (company name)
            fiscal_code: Unique fiscal/tax ID
            address: Street address
            city: City
            country: Country
            phone: Phone number (optional)
            email: Email address (optional)
            contact_person: Primary contact (optional)
            
        Returns:
            Created supplier
            
        Raises:
            ConflictException: If fiscal_code already exists
            ValidationException: If required fields invalid
        """
        # Check if fiscal_code already exists
        stmt = select(Supplier).where(Supplier.fiscal_code == fiscal_code).where(Supplier.deleted_at.is_(None))
        result = await db.execute(stmt)
        if result.scalars().first():
            raise ConflictException("Supplier", f"fiscal_code {fiscal_code} already exists")

        # Validate required fields
        if not name or len(name.strip()) == 0:
            raise ValidationException("Supplier name is required")
        if not fiscal_code or len(fiscal_code.strip()) == 0:
            raise ValidationException("Fiscal code is required")

        # Create supplier
        supplier = Supplier(
            name=name,
            fiscal_code=fiscal_code,
            address=address,
            city=city,
            country=country,
            phone=phone,
            email=email,
            contact_person=contact_person,
        )
        db.add(supplier)
        await db.commit()
        await db.refresh(supplier)

        return supplier

    async def get_supplier_by_id(self, db: AsyncSession, supplier_id: UUID) -> Supplier:
        """Get supplier by ID."""
        stmt = select(Supplier).where(Supplier.id == supplier_id).where(Supplier.deleted_at.is_(None))
        result = await db.execute(stmt)
        supplier = result.scalars().first()

        if not supplier:
            raise NotFoundException("Supplier", str(supplier_id))

        return supplier

    async def get_supplier_by_fiscal_code(self, db: AsyncSession, fiscal_code: str) -> Optional[Supplier]:
        """Get supplier by fiscal code."""
        stmt = select(Supplier).where(Supplier.fiscal_code == fiscal_code).where(Supplier.deleted_at.is_(None))
        result = await db.execute(stmt)
        return result.scalars().first()

    async def list_suppliers(
        self, db: AsyncSession, skip: int = 0, limit: int = 100, country: Optional[str] = None
    ) -> tuple[List[Supplier], int]:
        """List suppliers with pagination and optional filtering."""
        base_stmt = select(Supplier).where(Supplier.deleted_at.is_(None))
        if country:
            base_stmt = base_stmt.where(Supplier.country == country)

        count_stmt = select(func.count(Supplier.id)).select_from(Supplier).where(Supplier.deleted_at.is_(None))
        if country:
            count_stmt = count_stmt.where(Supplier.country == country)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = base_stmt.offset(skip).limit(limit).order_by(Supplier.created_at.desc())
        result = await db.execute(stmt)
        suppliers = result.scalars().all()

        return suppliers, total

    async def update_supplier(
        self,
        db: AsyncSession,
        supplier_id: UUID,
        name: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        contact_person: Optional[str] = None,
    ) -> Supplier:
        """Update supplier details."""
        supplier = await self.get_supplier_by_id(db, supplier_id)

        if name is not None:
            supplier.name = name
        if address is not None:
            supplier.address = address
        if city is not None:
            supplier.city = city
        if country is not None:
            supplier.country = country
        if phone is not None:
            supplier.phone = phone
        if email is not None:
            supplier.email = email
        if contact_person is not None:
            supplier.contact_person = contact_person

        db.add(supplier)
        await db.commit()
        await db.refresh(supplier)

        return supplier

    async def deactivate_supplier(self, db: AsyncSession, supplier_id: UUID) -> Supplier:
        """Deactivate a supplier (soft delete)."""
        supplier = await self.get_supplier_by_id(db, supplier_id)
        supplier.deleted_at = func.now()
        db.add(supplier)
        await db.commit()
        await db.refresh(supplier)

        return supplier

    async def delete_supplier(self, db: AsyncSession, supplier_id: UUID) -> None:
        """Delete a supplier permanently."""
        supplier = await self.get_supplier_by_id(db, supplier_id)
        await db.delete(supplier)
        await db.commit()
