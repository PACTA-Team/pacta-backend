"""
Authentication service - JWT, login, refresh tokens, password management
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.src.security import JWTHandler, hash_password, verify_password
from shared.src.exceptions import AuthException, NotFoundException
from src.models.user import User
from src.config import settings


class AuthService:
    """
    Service for authentication and authorization.
    Manages JWT tokens, passwords, login/logout.
    """

    def __init__(self):
        self.jwt_handler = JWTHandler(
            secret_key=settings.secret_key,
            algorithm=settings.jwt_algorithm,
            access_token_expire_minutes=settings.access_token_expire_minutes,
            refresh_token_expire_days=settings.refresh_token_expire_days,
        )

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """
        Authenticate user by email and password.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            User if authentication successful, None otherwise
            
        Raises:
            AuthException: If credentials are invalid
        """
        # Fetch user by email
        stmt = select(User).where(User.email == email).where(User.deleted_at.is_(None))
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise AuthException("Invalid credentials")

        if not user.is_active:
            raise AuthException("User account is disabled")

        # Verify password
        if not verify_password(password, user.password_hash):
            raise AuthException("Invalid credentials")

        return user

    async def create_tokens(self, user_id: str) -> dict:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user_id: User ID (UUID)
            
        Returns:
            Dict with access_token and refresh_token
        """
        data = {"sub": str(user_id), "type": "access"}
        access_token = self.jwt_handler.create_access_token(data)

        data = {"sub": str(user_id), "type": "refresh"}
        refresh_token = self.jwt_handler.create_refresh_token(data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
        }

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Create a new access token from a refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Dict with new access_token
            
        Raises:
            AuthException: If refresh token is invalid or expired
        """
        # Decode and validate refresh token
        payload = self.jwt_handler.decode_token(refresh_token)
        if not payload:
            raise AuthException("Invalid or expired refresh token")

        if not self.jwt_handler.verify_token_type(refresh_token, "refresh"):
            raise AuthException("Invalid token type")

        # Create new access token
        user_id = payload.get("sub")
        data = {"sub": user_id, "type": "access"}
        access_token = self.jwt_handler.create_access_token(data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
        }

    async def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify and decode an access token.
        
        Args:
            token: JWT token
            
        Returns:
            Payload if valid, None otherwise
        """
        payload = self.jwt_handler.decode_token(token)
        if not payload:
            return None

        if not self.jwt_handler.verify_token_type(token, "access"):
            return None

        return payload

    async def change_password(
        self, db: AsyncSession, user_id: str, old_password: str, new_password: str
    ) -> User:
        """
        Change user password.
        
        Args:
            db: Database session
            user_id: User ID
            old_password: Current password (plain text)
            new_password: New password (plain text)
            
        Returns:
            Updated user
            
        Raises:
            AuthException: If old password is wrong
            NotFoundException: If user not found
        """
        # Fetch user
        stmt = select(User).where(User.id == user_id).where(User.deleted_at.is_(None))
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise NotFoundException("User", user_id)

        # Verify old password
        if not verify_password(old_password, user.password_hash):
            raise AuthException("Current password is incorrect")

        # Hash and update new password
        user.password_hash = hash_password(new_password)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def get_current_user(self, db: AsyncSession, token: str) -> User:
        """
        Get current user from token.
        
        Args:
            db: Database session
            token: JWT token
            
        Returns:
            User object
            
        Raises:
            AuthException: If token invalid
            NotFoundException: If user not found
        """
        payload = await self.verify_token(token)
        if not payload:
            raise AuthException("Invalid token")

        user_id = payload.get("sub")
        stmt = select(User).where(User.id == user_id).where(User.deleted_at.is_(None))
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise NotFoundException("User", user_id)

        return user
