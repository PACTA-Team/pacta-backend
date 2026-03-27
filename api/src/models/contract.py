"""
Contract ORM model - Contratos (CORE del sistema)
"""
from datetime import date
from sqlalchemy import Column, String, Text, Boolean, Enum, ForeignKey, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import BaseModel
from shared.src.enums import ContractStatus, ContractType


class Contract(BaseModel):
    """
    Contrato - CORE del sistema PACTA.
    
    Campos:
    - contract_number: Número único de contrato - índice
    - title: Título del contrato
    - description: Descripción
    - client_id: FK a cliente - índice
    - supplier_id: FK a proveedor - índice
    - client_signatory_id: FK a firmante del cliente
    - supplier_signatory_id: FK a firmante del proveedor
    - start_date: Fecha inicio
    - end_date: Fecha fin - índice (para búsquedas de vencimiento)
    - amount: Monto monetario
    - contract_type: Tipo (service, supply, license, etc.) - índice
    - status: Estado (draft, pending, active, expired, cancelled, terminated) - índice
    - created_by: Usuario que creó - índice
    """

    __tablename__ = "contracts"

    contract_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relaciones con empresas
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    # Firmantes
    client_signatory_id = Column(UUID(as_uuid=True), ForeignKey("signatories.id", ondelete="RESTRICT"), nullable=False)
    supplier_signatory_id = Column(UUID(as_uuid=True), ForeignKey("signatories.id", ondelete="RESTRICT"), nullable=False)
    
    # Fechas y montos
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    
    # Clasificación
    contract_type = Column(Enum(ContractType), nullable=False, default=ContractType.SERVICE, index=True)
    status = Column(Enum(ContractStatus), nullable=False, default=ContractStatus.DRAFT, index=True)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Contract(id={self.id}, contract_number={self.contract_number}, status={self.status})>"

    def is_expired(self) -> bool:
        """Check if contract is expired (end_date < today)."""
        from datetime import datetime
        return self.end_date < date.today()

    def can_activate(self) -> bool:
        """Check if contract can be activated."""
        return self.status == ContractStatus.DRAFT and not self.is_expired()
