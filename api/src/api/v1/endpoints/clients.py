"""
Client management API endpoints
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from src.db.session import get_db
from src.services.client import ClientService
from shared.src.exceptions import NotFoundException, ConflictException, ValidationException

router = APIRouter(prefix="/clients", tags=["clients"])
client_service = ClientService()


# Request/Response schemas
class ClientCreateRequest(BaseModel):
    """Create client request."""

    name: str
    fiscal_code: str
    address: str
    city: str
    country: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    contact_person: Optional[str] = None

    class Config:
        example = {
            "name": "Acme Corporation",
            "fiscal_code": "IT12345678",
            "address": "123 Business St",
            "city": "Rome",
            "country": "Italy",
            "phone": "+39-06-1234567",
            "email": "contact@acme.it",
            "contact_person": "John Rossi",
        }


class ClientUpdateRequest(BaseModel):
    """Update client request."""

    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    contact_person: Optional[str] = None

    class Config:
        example = {
            "name": "Acme Corp Updated",
            "phone": "+39-06-9999999",
        }


class ClientResponse(BaseModel):
    """Client response."""

    id: UUID
    name: str
    fiscal_code: str
    address: str
    city: str
    country: str
    phone: Optional[str]
    email: Optional[str]
    contact_person: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
        example = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Acme Corporation",
            "fiscal_code": "IT12345678",
            "address": "123 Business St",
            "city": "Rome",
            "country": "Italy",
            "phone": "+39-06-1234567",
            "email": "contact@acme.it",
            "contact_person": "John Rossi",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }


class ClientListResponse(BaseModel):
    """Client list response."""

    clients: list[ClientResponse]
    total: int
    skip: int
    limit: int


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(request: ClientCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a new client.
    
    - **name**: Company name
    - **fiscal_code**: Unique tax/fiscal ID
    - **address**: Street address
    - **city**: City
    - **country**: Country
    - **phone**: Phone number (optional)
    - **email**: Email address (optional)
    - **contact_person**: Primary contact name (optional)
    """
    try:
        client = await client_service.create_client(
            db,
            request.name,
            request.fiscal_code,
            request.address,
            request.city,
            request.country,
            request.phone,
            request.email,
            request.contact_person,
        )
        return client
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{client_id}", response_model=ClientResponse, status_code=status.HTTP_200_OK)
async def get_client(client_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get a client by ID.
    """
    try:
        client = await client_service.get_client_by_id(db, client_id)
        return client
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=ClientListResponse, status_code=status.HTTP_200_OK)
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    country: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    List all clients with pagination and optional filtering.
    
    - **skip**: Number of clients to skip (default: 0)
    - **limit**: Maximum clients to return (default: 100, max: 1000)
    - **country**: Filter by country (optional)
    """
    try:
        clients, total = await client_service.list_clients(db, skip, limit, country)
        return {
            "clients": clients,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{client_id}", response_model=ClientResponse, status_code=status.HTTP_200_OK)
async def update_client(
    client_id: UUID, request: ClientUpdateRequest, db: AsyncSession = Depends(get_db)
):
    """
    Update a client.
    """
    try:
        client = await client_service.update_client(
            db,
            client_id,
            request.name,
            request.address,
            request.city,
            request.country,
            request.phone,
            request.email,
            request.contact_person,
        )
        return client
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{client_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_client(client_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Delete a client (soft delete).
    """
    try:
        await client_service.deactivate_client(db, client_id)
        return {"message": f"Client {client_id} deleted successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
