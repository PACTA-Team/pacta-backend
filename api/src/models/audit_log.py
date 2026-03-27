"""
AuditLog ORM model - Registro completo de auditoría para compliance
"""
from sqlalchemy import Column, String, Text, Enum, ForeignKey, INET
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.models.base import BaseModel
from shared.src.enums import AuditAction


class AuditLog(BaseModel):
    """
    Log de auditoría - registro de TODAS las operaciones (create, update, delete).
    
    Propósito: Compliance, trazabilidad, seguridad, debugging.
    
    Campos:
    - user_id: FK a usuario que realizó la acción
    - action: Tipo (CREATE, UPDATE, DELETE)
    - entity_type: Tipo de entidad (contract, client, supplement, etc.)
    - entity_id: ID de la entidad afectada
    - old_values: JSON con estado anterior (para UPDATE/DELETE)
    - new_values: JSON con estado nuevo (para CREATE/UPDATE)
    - description: Descripción de la acción
    - ip_address: IP del cliente (para seguridad)
    - user_agent: User-Agent del navegador/cliente
    
    Nota: timestamp (created_at) es automático del BaseModel.
    """

    __tablename__ = "audit_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(Enum(AuditAction), nullable=False, index=True)
    
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    
    description = Column(Text, nullable=True)
    
    ip_address = Column(String(45), nullable=True)  # IPv4 (15) + IPv6 (39)
    user_agent = Column(String(500), nullable=True)

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, entity_type={self.entity_type})>"

    @staticmethod
    def from_create(
        user_id, entity_type: str, entity_id, new_values: dict, description: str = None, ip_address: str = None, user_agent: str = None
    ) -> "AuditLog":
        """Factory method for CREATE action."""
        return AuditLog(
            user_id=user_id,
            action=AuditAction.CREATE,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=None,
            new_values=new_values,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def from_update(
        user_id, entity_type: str, entity_id, old_values: dict, new_values: dict, description: str = None, ip_address: str = None, user_agent: str = None
    ) -> "AuditLog":
        """Factory method for UPDATE action."""
        return AuditLog(
            user_id=user_id,
            action=AuditAction.UPDATE,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def from_delete(
        user_id, entity_type: str, entity_id, old_values: dict, description: str = None, ip_address: str = None, user_agent: str = None
    ) -> "AuditLog":
        """Factory method for DELETE action."""
        return AuditLog(
            user_id=user_id,
            action=AuditAction.DELETE,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=None,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
        )
