"""
User service - CRUD operations and business logic
"""
from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.models.user import User
from shared.src.exceptions import NotFoundException, ConflictException, ValidationException
from shared.src.security import hash_password
from shared.src.enums import UserRole


class UserService:
    """Service for user management."""

    async def create_user(
        self, db: AsyncSession, email: str, password: str, role: UserRole = UserRole.USER
    ) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            email: User email (must be unique)
            password: Plain text password
            role: User role (default: USER)
            
        Returns:
            Created user
            
        Raises:
            ConflictException: If email already exists
            ValidationException: If password is invalid
        """
        # Check if email already exists
        stmt = select(User).where(User.email == email).where(User.deleted_at.is_(None))
        result = await db.execute(stmt)
        if result.scalars().first():
            raise ConflictException("User", f"email {email} already exists")

        # Validate password
        if len(password) < 8:
            raise ValidationException("Password must be at least 8 characters")

        # Create user
        user = User(
            email=email,
            password_hash=hash_password(password),
            role=role,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def get_user_by_id(self, db: AsyncSession, user_id: UUID) -> User:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User object
            
        Raises:
            NotFoundException: If user not found
        """
        stmt = select(User).where(User.id == user_id).where(User.deleted_at.is_(None))
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise NotFoundException("User", str(user_id))

        return user

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User object if found, None otherwise
        """
        stmt = select(User).where(User.email == email).where(User.deleted_at.is_(None))
        result = await db.execute(stmt)
        return result.scalars().first()

    async def list_users(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> tuple[List[User], int]:
        """
        List all users with pagination.
        
        Args:
            db: Database session
            skip: Number of users to skip
            limit: Maximum users to return
            
        Returns:
            Tuple of (users list, total count)
        """
        # Get total count
        count_stmt = select(func.count(User.id)).where(User.deleted_at.is_(None))
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated users
        stmt = (
            select(User)
            .where(User.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        result = await db.execute(stmt)
        users = result.scalars().all()

        return users, total

    async def update_user(
        self, db: AsyncSession, user_id: UUID, email: Optional[str] = None, role: Optional[UserRole] = None
    ) -> User:
        """
        Update user details.
        
        Args:
            db: Database session
            user_id: User ID
            email: New email (optional)
            role: New role (optional)
            
        Returns:
            Updated user
            
        Raises:
            NotFoundException: If user not found
            ConflictException: If email already exists
        """
        user = await self.get_user_by_id(db, user_id)

        # Check if new email is unique
        if email and email != user.email:
            stmt = select(User).where(User.email == email).where(User.deleted_at.is_(None))
            result = await db.execute(stmt)
            if result.scalars().first():
                raise ConflictException("User", f"email {email} already exists")
            user.email = email

        if role:
            user.role = role

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def deactivate_user(self, db: AsyncSession, user_id: UUID) -> User:
        """
        Deactivate a user (soft delete).
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Updated user
            
        Raises:
            NotFoundException: If user not found
        """
        user = await self.get_user_by_id(db, user_id)
        user.is_active = False
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def delete_user(self, db: AsyncSession, user_id: UUID) -> None:
        """
        Delete a user (hard delete - use soft delete for audit trail).
        
        Args:
            db: Database session
            user_id: User ID
            
        Raises:
            NotFoundException: If user not found
        """
        user = await self.get_user_by_id(db, user_id)
        await db.delete(user)
        await db.commit()
