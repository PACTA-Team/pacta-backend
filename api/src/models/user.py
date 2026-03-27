"""
User ORM model - Sistema de usuarios y autenticación
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import BaseModel
from shared.src.enums import UserRole


class User(BaseModel):
    """
    Usuario del sistema para autenticación y autorización.
    
    Campos:
    - email: Email único (índice)
    - password_hash: Hash de contraseña (bcrypt)
    - first_name: Nombre
    - last_name: Apellido
    - role: Rol (admin, manager, editor, viewer) - índice
    - is_active: Usuario activo - índice
    - last_login: Último login
    """

    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def can_manage(self) -> bool:
        return self.role in (UserRole.MANAGER, UserRole.ADMIN)

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
