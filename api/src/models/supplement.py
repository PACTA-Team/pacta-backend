"""
Supplement ORM model - Suplementos/Adendas contractuales
"""
from datetime import date, datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, Enum, ForeignKey, Date, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.models.base import BaseModel
from shared.src.enums import SupplementStatus


class Supplement(BaseModel):
    """
    Suplemento/Adenda contractual - modificaciones formales a contratos.
    
    Campos:
    - contract_id: FK a contrato - índice
    - supplement_number: Número secuencial (SUP-001, etc.)
    - description: Descripción de modificaciones
    - modifications_detail: JSON con detalles de cambios
    - effective_date: Fecha en que entra en vigencia
    - status: Estado (draft, approved, active, cancelled) - índice
    - client_signatory_id: FK a firmante del cliente
    - supplier_signatory_id: FK a firmante del proveedor
    - approved_by: FK a usuario que aprobó
    - approved_at: Timestamp de aprobación
    - created_by: FK a usuario que creó
    """

    __tablename__ = "supplements"

    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True)
    supplement_number = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    modifications_detail = Column(JSONB, nullable=True)
    effective_date = Column(Date, nullable=False, index=True)
    
    status = Column(Enum(SupplementStatus), nullable=False, default=SupplementStatus.DRAFT, index=True)
    
    # Firmantes
    client_signatory_id = Column(UUID(as_uuid=True), ForeignKey("signatories.id", ondelete="RESTRICT"), nullable=False)
    supplier_signatory_id = Column(UUID(as_uuid=True), ForeignKey("signatories.id", ondelete="RESTRICT"), nullable=False)
    
    # Aprobación
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)

    __table_args__ = (
        # Unique constraint: supplement_number es único por contrato
        __import__('sqlalchemy').UniqueConstraint('contract_id', 'supplement_number', name='uq_contract_supplement_number'),
    )

    def __repr__(self) -> str:
        return f"<Supplement(id={self.id}, supplement_number={self.supplement_number}, status={self.status})>"

    def approve(self, approved_by_id) -> None:
        """Mark supplement as approved."""
        self.status = SupplementStatus.APPROVED
        self.approved_by = approved_by_id
        self.approved_at = datetime.now(timezone.utc)
