"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from src.db.session import get_db
from src.services.auth import AuthService
from shared.src.exceptions import AuthException, NotFoundException

router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()


# Request/Response schemas
class LoginRequest(BaseModel):
    """Login request."""

    email: EmailStr
    password: str

    class Config:
        example = {
            "email": "user@example.com",
            "password": "SecurePassword123!",
        }


class TokenResponse(BaseModel):
    """Token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AccessTokenResponse(BaseModel):
    """Access token response (refresh endpoint)."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Change password request."""

    old_password: str
    new_password: str


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


@router.post("/login", response_model=TokenResponse, status_code=200)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login with email and password.
    
    Returns access token and refresh token.
    """
    try:
        user = await auth_service.authenticate_user(db, request.email, request.password)
        tokens = await auth_service.create_tokens(user.id)
        return tokens
    except AuthException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/refresh", response_model=AccessTokenResponse, status_code=200)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using a valid refresh token.
    """
    try:
        tokens = await auth_service.refresh_access_token(request.refresh_token)
        return tokens
    except AuthException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/logout", response_model=MessageResponse, status_code=200)
async def logout():
    """
    Logout (invalidate token on client side).
    
    Note: JWT tokens are stateless. Logout is typically handled by
    the client discarding the token. For more complex logout scenarios,
    implement a token blacklist in Redis.
    """
    return {"message": "Logged out successfully"}
