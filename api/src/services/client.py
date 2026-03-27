"""
Client service - CRUD operations and business logic
"""
from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.models.client import Client
from shared.src.exceptions import NotFoundException, ConflictException, ValidationException


class ClientService:
    """Service for client management."""

    async def create_client(
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
    ) -> Client:
        """
        Create a new client.
        
        Args:
            db: Database session
            name: Client name (company name)
            fiscal_code: Unique fiscal/tax ID
            address: Street address
            city: City
            country: Country
            phone: Phone number (optional)
            email: Email address (optional)
            contact_person: Primary contact (optional)
            
        Returns:
            Created client
            
        Raises:
            ConflictException: If fiscal_code already exists
            ValidationException: If required fields invalid
        """
        # Check if fiscal_code already exists
        stmt = select(Client).where(Client.fiscal_code == fiscal_code).where(Client.deleted_at.is_(None))
        result = await db.execute(stmt)
        if result.scalars().first():
            raise ConflictException("Client", f"fiscal_code {fiscal_code} already exists")

        # Validate required fields
        if not name or len(name.strip()) == 0:
            raise ValidationException("Client name is required")
        if not fiscal_code or len(fiscal_code.strip()) == 0:
            raise ValidationException("Fiscal code is required")

        # Create client
        client = Client(
            name=name,
            fiscal_code=fiscal_code,
            address=address,
            city=city,
            country=country,
            phone=phone,
            email=email,
            contact_person=contact_person,
        )
        db.add(client)
        await db.commit()
        await db.refresh(client)

        return client

    async def get_client_by_id(self, db: AsyncSession, client_id: UUID) -> Client:
        """
        Get client by ID.
        
        Args:
            db: Database session
            client_id: Client ID
            
        Returns:
            Client object
            
        Raises:
            NotFoundException: If client not found
        """
        stmt = select(Client).where(Client.id == client_id).where(Client.deleted_at.is_(None))
        result = await db.execute(stmt)
        client = result.scalars().first()

        if not client:
            raise NotFoundException("Client", str(client_id))

        return client

    async def get_client_by_fiscal_code(self, db: AsyncSession, fiscal_code: str) -> Optional[Client]:
        """
        Get client by fiscal code.
        
        Args:
            db: Database session
            fiscal_code: Fiscal code
            
        Returns:
            Client object if found, None otherwise
        """
        stmt = select(Client).where(Client.fiscal_code == fiscal_code).where(Client.deleted_at.is_(None))
        result = await db.execute(stmt)
        return result.scalars().first()

    async def list_clients(
        self, db: AsyncSession, skip: int = 0, limit: int = 100, country: Optional[str] = None
    ) -> tuple[List[Client], int]:
        """
        List clients with pagination and optional filtering.
        
        Args:
            db: Database session
            skip: Number of clients to skip
            limit: Maximum clients to return
            country: Filter by country (optional)
            
        Returns:
            Tuple of (clients list, total count)
        """
        # Build query
        base_stmt = select(Client).where(Client.deleted_at.is_(None))
        if country:
            base_stmt = base_stmt.where(Client.country == country)

        # Get total count
        count_stmt = select(func.count(Client.id)).select_from(Client).where(Client.deleted_at.is_(None))
        if country:
            count_stmt = count_stmt.where(Client.country == country)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated clients
        stmt = base_stmt.offset(skip).limit(limit).order_by(Client.created_at.desc())
        result = await db.execute(stmt)
        clients = result.scalars().all()

        return clients, total

    async def update_client(
        self,
        db: AsyncSession,
        client_id: UUID,
        name: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        contact_person: Optional[str] = None,
    ) -> Client:
        """
        Update client details.
        
        Args:
            db: Database session
            client_id: Client ID
            name: New name (optional)
            address: New address (optional)
            city: New city (optional)
            country: New country (optional)
            phone: New phone (optional)
            email: New email (optional)
            contact_person: New contact person (optional)
            
        Returns:
            Updated client
            
        Raises:
            NotFoundException: If client not found
        """
        client = await self.get_client_by_id(db, client_id)

        if name is not None:
            client.name = name
        if address is not None:
            client.address = address
        if city is not None:
            client.city = city
        if country is not None:
            client.country = country
        if phone is not None:
            client.phone = phone
        if email is not None:
            client.email = email
        if contact_person is not None:
            client.contact_person = contact_person

        db.add(client)
        await db.commit()
        await db.refresh(client)

        return client

    async def deactivate_client(self, db: AsyncSession, client_id: UUID) -> Client:
        """
        Deactivate a client (soft delete).
        
        Args:
            db: Database session
            client_id: Client ID
            
        Returns:
            Updated client
            
        Raises:
            NotFoundException: If client not found
        """
        client = await self.get_client_by_id(db, client_id)
        client.deleted_at = func.now()
        db.add(client)
        await db.commit()
        await db.refresh(client)

        return client

    async def delete_client(self, db: AsyncSession, client_id: UUID) -> None:
        """
        Delete a client permanently.
        
        Args:
            db: Database session
            client_id: Client ID
            
        Raises:
            NotFoundException: If client not found
        """
        client = await self.get_client_by_id(db, client_id)
        await db.delete(client)
        await db.commit()
