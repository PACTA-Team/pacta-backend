"""
Supplier management API endpoints
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from src.db.session import get_db
from src.services.supplier import SupplierService
from shared.src.exceptions import NotFoundException, ConflictException, ValidationException

router = APIRouter(prefix="/suppliers", tags=["suppliers"])
supplier_service = SupplierService()


# Request/Response schemas (similar to Client)
class SupplierCreateRequest(BaseModel):
    """Create supplier request."""

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
            "name": "TechVendor Solutions",
            "fiscal_code": "IT98765432",
            "address": "456 Tech Drive",
            "city": "Milan",
            "country": "Italy",
            "phone": "+39-02-5555555",
            "email": "sales@techvendor.it",
            "contact_person": "Maria Bianchi",
        }


class SupplierUpdateRequest(BaseModel):
    """Update supplier request."""

    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    contact_person: Optional[str] = None


class SupplierResponse(BaseModel):
    """Supplier response."""

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


class SupplierListResponse(BaseModel):
    """Supplier list response."""

    suppliers: list[SupplierResponse]
    total: int
    skip: int
    limit: int


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(request: SupplierCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a new supplier.
    """
    try:
        supplier = await supplier_service.create_supplier(
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
        return supplier
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{supplier_id}", response_model=SupplierResponse, status_code=status.HTTP_200_OK)
async def get_supplier(supplier_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a supplier by ID."""
    try:
        supplier = await supplier_service.get_supplier_by_id(db, supplier_id)
        return supplier
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=SupplierListResponse, status_code=status.HTTP_200_OK)
async def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    country: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all suppliers with pagination and optional filtering."""
    try:
        suppliers, total = await supplier_service.list_suppliers(db, skip, limit, country)
        return {
            "suppliers": suppliers,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{supplier_id}", response_model=SupplierResponse, status_code=status.HTTP_200_OK)
async def update_supplier(
    supplier_id: UUID, request: SupplierUpdateRequest, db: AsyncSession = Depends(get_db)
):
    """Update a supplier."""
    try:
        supplier = await supplier_service.update_supplier(
            db,
            supplier_id,
            request.name,
            request.address,
            request.city,
            request.country,
            request.phone,
            request.email,
            request.contact_person,
        )
        return supplier
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{supplier_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_supplier(supplier_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a supplier (soft delete)."""
    try:
        await supplier_service.deactivate_supplier(db, supplier_id)
        return {"message": f"Supplier {supplier_id} deleted successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
