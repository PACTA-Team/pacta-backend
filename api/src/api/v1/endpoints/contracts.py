"""
Contract management API endpoints
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.db.session import get_db
from src.services.contract import ContractService
from shared.src.exceptions import NotFoundException, ConflictException, ValidationException
from shared.src.enums import ContractStatus, ContractType

router = APIRouter(prefix="/contracts", tags=["contracts"])
contract_service = ContractService()


# Request/Response schemas
class ContractCreateRequest(BaseModel):
    """Create contract request."""

    client_id: UUID
    supplier_id: UUID
    contract_number: str
    title: str
    amount: float
    contract_type: ContractType
    start_date: datetime
    end_date: datetime
    description: Optional[str] = None
    client_signatory_id: Optional[UUID] = None
    supplier_signatory_id: Optional[UUID] = None

    class Config:
        example = {
            "client_id": "123e4567-e89b-12d3-a456-426614174000",
            "supplier_id": "223e4567-e89b-12d3-a456-426614174000",
            "contract_number": "CNT-2024-001",
            "title": "Software License Agreement",
            "amount": 50000.00,
            "contract_type": "LICENSE",
            "start_date": "2024-01-01T00:00:00",
            "end_date": "2025-12-31T23:59:59",
            "description": "Annual software license for 50 users",
        }


class ContractUpdateRequest(BaseModel):
    """Update contract request."""

    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    client_signatory_id: Optional[UUID] = None
    supplier_signatory_id: Optional[UUID] = None


class ContractStatusChangeRequest(BaseModel):
    """Change contract status request."""

    status: ContractStatus


class ContractResponse(BaseModel):
    """Contract response."""

    id: UUID
    client_id: UUID
    supplier_id: UUID
    contract_number: str
    title: str
    amount: float
    contract_type: str
    status: str
    start_date: str
    end_date: str
    description: Optional[str]
    client_signatory_id: Optional[UUID]
    supplier_signatory_id: Optional[UUID]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ContractListResponse(BaseModel):
    """Contract list response."""

    contracts: list[ContractResponse]
    total: int
    skip: int
    limit: int


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


@router.post("", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(request: ContractCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a new contract.
    """
    try:
        contract = await contract_service.create_contract(
            db,
            request.client_id,
            request.supplier_id,
            request.contract_number,
            request.title,
            request.amount,
            request.contract_type,
            request.start_date,
            request.end_date,
            request.description,
            request.client_signatory_id,
            request.supplier_signatory_id,
        )
        return contract
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{contract_id}", response_model=ContractResponse, status_code=status.HTTP_200_OK)
async def get_contract(contract_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a contract by ID."""
    try:
        contract = await contract_service.get_contract_by_id(db, contract_id)
        return contract
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=ContractListResponse, status_code=status.HTTP_200_OK)
async def list_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ContractStatus] = Query(None),
    client_id: Optional[UUID] = Query(None),
    supplier_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all contracts with pagination and optional filtering."""
    try:
        contracts, total = await contract_service.list_contracts(
            db, skip, limit, status, client_id, supplier_id
        )
        return {
            "contracts": contracts,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{contract_id}", response_model=ContractResponse, status_code=status.HTTP_200_OK)
async def update_contract(
    contract_id: UUID, request: ContractUpdateRequest, db: AsyncSession = Depends(get_db)
):
    """Update a contract."""
    try:
        contract = await contract_service.update_contract(
            db,
            contract_id,
            request.title,
            request.description,
            request.amount,
            request.start_date,
            request.end_date,
            request.client_signatory_id,
            request.supplier_signatory_id,
        )
        return contract
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{contract_id}/status", response_model=ContractResponse, status_code=status.HTTP_200_OK)
async def change_contract_status(
    contract_id: UUID, request: ContractStatusChangeRequest, db: AsyncSession = Depends(get_db)
):
    """Change contract status."""
    try:
        contract = await contract_service.change_status(db, contract_id, request.status)
        return contract
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/expiring/soon", response_model=list[ContractResponse], status_code=status.HTTP_200_OK)
async def get_expiring_contracts(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get contracts expiring within N days."""
    try:
        contracts = await contract_service.get_expiring_contracts(db, days)
        return contracts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{contract_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_contract(contract_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a contract (soft delete)."""
    try:
        await contract_service.deactivate_contract(db, contract_id)
        return {"message": f"Contract {contract_id} deleted successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
