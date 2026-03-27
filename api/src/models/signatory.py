"""
Signatory ORM model - Firmantes autorizados (polimórfico)
"""
from sqlalchemy import Column, String, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import BaseModel
from shared.src.enums import EntityType, IdentityType


class Signatory(BaseModel):
    """
    Firmante autorizado (persona que puede firmar por una empresa).
    
    Relación polimórfica: puede estar asociado a un cliente O proveedor.
    
    Campos:
    - entity_type: Tipo (client o supplier) - índice compuesto
    - entity_id: ID de la empresa (client_id o supplier_id) - índice compuesto
    - first_name: Nombre
    - last_name: Apellido
    - title: Cargo/título
    - email: Email - índice
    - phone: Teléfono
    - identity_document: Documento de identidad
    - identity_type: Tipo documento (dni, passport, rut, other)
    - is_active: Activo - índice
    """

    __tablename__ = "signatories"

    entity_type = Column(Enum(EntityType), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    title = Column(String(100), nullable=True)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    identity_document = Column(String(50), nullable=False)
    identity_type = Column(Enum(IdentityType), nullable=False, default=IdentityType.DNI)
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    def __repr__(self) -> str:
        return f"<Signatory(id={self.id}, email={self.email}, entity_type={self.entity_type})>"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
