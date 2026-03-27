"""
Signatory management API endpoints
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from src.db.session import get_db
from src.services.signatory import SignatoryService
from shared.src.exceptions import NotFoundException, ConflictException, ValidationException
from shared.src.enums import IdentityType

router = APIRouter(prefix="/signatories", tags=["signatories"])
signatory_service = SignatoryService()


# Request/Response schemas
class SignatoryCreateRequest(BaseModel):
    """Create signatory request."""

    entity_type: IdentityType
    entity_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    position: Optional[str] = None
    identity_document: Optional[str] = None

    class Config:
        example = {
            "entity_type": "CLIENT",
            "entity_id": "123e4567-e89b-12d3-a456-426614174000",
            "first_name": "John",
            "last_name": "Rossi",
            "email": "john.rossi@example.com",
            "phone": "+39-06-1234567",
            "position": "CEO",
            "identity_document": "AB123456CD",
        }


class SignatoryUpdateRequest(BaseModel):
    """Update signatory request."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    identity_document: Optional[str] = None


class SignatoryResponse(BaseModel):
    """Signatory response."""

    id: UUID
    entity_type: str
    entity_id: UUID
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    position: Optional[str]
    identity_document: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class SignatoryListResponse(BaseModel):
    """Signatory list response."""

    signatories: list[SignatoryResponse]
    total: int
    skip: int
    limit: int


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


@router.post("", response_model=SignatoryResponse, status_code=status.HTTP_201_CREATED)
async def create_signatory(request: SignatoryCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a new signatory (authorized signer).
    """
    try:
        signatory = await signatory_service.create_signatory(
            db,
            request.entity_type,
            request.entity_id,
            request.first_name,
            request.last_name,
            request.email,
            request.phone,
            request.position,
            request.identity_document,
        )
        return signatory
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{signatory_id}", response_model=SignatoryResponse, status_code=status.HTTP_200_OK)
async def get_signatory(signatory_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a signatory by ID."""
    try:
        signatory = await signatory_service.get_signatory_by_id(db, signatory_id)
        return signatory
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/entity/{entity_type}/{entity_id}", response_model=SignatoryListResponse, status_code=status.HTTP_200_OK)
async def list_signatories_by_entity(
    entity_type: IdentityType,
    entity_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """List signatories for a specific entity (client/supplier)."""
    try:
        signatories, total = await signatory_service.list_signatories_by_entity(
            db, entity_type, entity_id, skip, limit
        )
        return {
            "signatories": signatories,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{signatory_id}", response_model=SignatoryResponse, status_code=status.HTTP_200_OK)
async def update_signatory(
    signatory_id: UUID, request: SignatoryUpdateRequest, db: AsyncSession = Depends(get_db)
):
    """Update a signatory."""
    try:
        signatory = await signatory_service.update_signatory(
            db,
            signatory_id,
            request.first_name,
            request.last_name,
            request.email,
            request.phone,
            request.position,
            request.identity_document,
        )
        return signatory
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{signatory_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_signatory(signatory_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a signatory (soft delete)."""
    try:
        await signatory_service.deactivate_signatory(db, signatory_id)
        return {"message": f"Signatory {signatory_id} deleted successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
