"""
Notification ORM model - Notificaciones automáticas del sistema
"""
from sqlalchemy import Column, String, Text, Boolean, Enum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import BaseModel
from shared.src.enums import NotificationType


class Notification(BaseModel):
    """
    Notificación del sistema para usuarios.
    
    Generadas automáticamente por:
    - APScheduler: vencimientos de contratos, reminders de suplementos
    - Eventos manuales: cambios de estado, documentos subidos
    
    Campos:
    - user_id: FK a usuario destinatario
    - type: Tipo (contract_expiring, supplement_pending, status_changed, document_uploaded)
    - entity_type: Tipo de entidad referenciada
    - entity_id: ID de entidad referenciada
    - title: Título de la notificación
    - message: Mensaje detallado
    - is_read: Leída o no
    - read_at: Timestamp de lectura
    """

    __tablename__ = "notifications"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type={self.type}, is_read={self.is_read})>"

    def mark_as_read(self) -> None:
        """Mark notification as read."""
        from datetime import datetime, timezone
        self.is_read = True
        self.read_at = datetime.now(timezone.utc)

    def mark_as_unread(self) -> None:
        """Mark notification as unread."""
        self.is_read = False
        self.read_at = None
