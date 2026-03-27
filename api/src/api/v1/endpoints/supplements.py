"""
Supplement (contract amendment) API endpoints
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.db.session import get_db
from src.services.supplement import SupplementService
from shared.src.exceptions import NotFoundException, ValidationException
from shared.src.enums import SupplementStatus

router = APIRouter(prefix="/supplements", tags=["supplements"])
supplement_service = SupplementService()


# Request/Response schemas
class SupplementCreateRequest(BaseModel):
    """Create supplement request."""

    contract_id: UUID
    title: str
    description: Optional[str] = None
    modifications_detail: Optional[dict] = None

    class Config:
        example = {
            "contract_id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Extension Amendment",
            "description": "Extend contract by 12 months",
            "modifications_detail": {
                "extended_end_date": "2025-12-31",
                "new_amount": 55000.00,
                "reason": "Performance bonus",
            },
        }


class SupplementUpdateRequest(BaseModel):
    """Update supplement request."""

    title: Optional[str] = None
    description: Optional[str] = None
    modifications_detail: Optional[dict] = None


class SupplementStatusChangeRequest(BaseModel):
    """Change supplement status request."""

    status: SupplementStatus


class SupplementResponse(BaseModel):
    """Supplement response."""

    id: UUID
    contract_id: UUID
    title: str
    description: Optional[str]
    status: str
    modifications_detail: dict
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class SupplementListResponse(BaseModel):
    """Supplement list response."""

    supplements: list[SupplementResponse]
    total: int
    skip: int
    limit: int


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


@router.post("", response_model=SupplementResponse, status_code=status.HTTP_201_CREATED)
async def create_supplement(request: SupplementCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a new supplement (contract amendment).
    """
    try:
        supplement = await supplement_service.create_supplement(
            db,
            request.contract_id,
            request.title,
            request.description,
            request.modifications_detail,
        )
        return supplement
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{supplement_id}", response_model=SupplementResponse, status_code=status.HTTP_200_OK)
async def get_supplement(supplement_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a supplement by ID."""
    try:
        supplement = await supplement_service.get_supplement_by_id(db, supplement_id)
        return supplement
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/contract/{contract_id}", response_model=SupplementListResponse, status_code=status.HTTP_200_OK)
async def list_supplements_by_contract(
    contract_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[SupplementStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List supplements for a specific contract."""
    try:
        supplements, total = await supplement_service.list_supplements_by_contract(
            db, contract_id, skip, limit, status
        )
        return {
            "supplements": supplements,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{supplement_id}", response_model=SupplementResponse, status_code=status.HTTP_200_OK)
async def update_supplement(
    supplement_id: UUID, request: SupplementUpdateRequest, db: AsyncSession = Depends(get_db)
):
    """Update a supplement."""
    try:
        supplement = await supplement_service.update_supplement(
            db,
            supplement_id,
            request.title,
            request.description,
            request.modifications_detail,
        )
        return supplement
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{supplement_id}/status", response_model=SupplementResponse, status_code=status.HTTP_200_OK)
async def change_supplement_status(
    supplement_id: UUID, request: SupplementStatusChangeRequest, db: AsyncSession = Depends(get_db)
):
    """Change supplement status."""
    try:
        supplement = await supplement_service.change_status(db, supplement_id, request.status)
        return supplement
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{supplement_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_supplement(supplement_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a supplement (soft delete)."""
    try:
        await supplement_service.deactivate_supplement(db, supplement_id)
        return {"message": f"Supplement {supplement_id} deleted successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
