"""
User management API endpoints
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from src.db.session import get_db
from src.services.user import UserService
from src.services.auth import AuthService
from shared.src.exceptions import NotFoundException, ConflictException, ValidationException, AuthException
from shared.src.enums import UserRole

router = APIRouter(prefix="/users", tags=["users"])
user_service = UserService()
auth_service = AuthService()


# Request/Response schemas
class UserCreateRequest(BaseModel):
    """Create user request."""

    email: EmailStr
    password: str
    role: UserRole = UserRole.USER

    class Config:
        example = {
            "email": "user@example.com",
            "password": "SecurePassword123!",
            "role": "USER",
        }


class UserUpdateRequest(BaseModel):
    """Update user request."""

    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None

    class Config:
        example = {
            "email": "newemail@example.com",
            "role": "ADMIN",
        }


class UserResponse(BaseModel):
    """User response."""

    id: UUID
    email: str
    role: str
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
        example = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "role": "USER",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }


class UserListResponse(BaseModel):
    """User list response."""

    users: list[UserResponse]
    total: int
    skip: int
    limit: int


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(request: UserCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a new user.
    
    - **email**: User email (must be unique)
    - **password**: Minimum 8 characters
    - **role**: USER (default) or ADMIN
    """
    try:
        user = await user_service.create_user(db, request.email, request.password, request.role)
        return user
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get a user by ID.
    """
    try:
        user = await user_service.get_user_by_id(db, user_id)
        return user
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    List all users with pagination.
    
    - **skip**: Number of users to skip (default: 0)
    - **limit**: Maximum users to return (default: 100, max: 1000)
    """
    try:
        users, total = await user_service.list_users(db, skip, limit)
        return {
            "users": users,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID, request: UserUpdateRequest, db: AsyncSession = Depends(get_db)
):
    """
    Update a user.
    
    - **email**: New email (optional)
    - **role**: New role (optional)
    """
    try:
        user = await user_service.update_user(db, user_id, request.email, request.role)
        return user
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{user_id}/deactivate", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def deactivate_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Deactivate a user (soft delete).
    """
    try:
        user = await user_service.deactivate_user(db, user_id)
        return user
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{user_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Delete a user (hard delete).
    
    **Warning**: This permanently removes the user from the database.
    Use deactivate_user for audit trail preservation.
    """
    try:
        await user_service.delete_user(db, user_id)
        return {"message": f"User {user_id} deleted successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
