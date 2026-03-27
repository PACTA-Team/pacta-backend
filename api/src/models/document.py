"""
Document ORM model - Documentos/Archivos adjuntos (polimórfico)
"""
from sqlalchemy import Column, String, BigInteger, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import BaseModel
from shared.src.enums import EntityType


class Document(BaseModel):
    """
    Documento/Archivo adjunto (relación polimórfica).
    
    Puede asociarse a: contract, client, supplier, supplement
    Los archivos se almacenan en MinIO/S3 con clave s3_key.
    
    Campos:
    - entity_type: Tipo de entidad (contract, client, supplier, supplement)
    - entity_id: ID de la entidad
    - file_name: Nombre del archivo
    - file_size: Tamaño en bytes
    - mime_type: Tipo MIME (pdf, docx, xlsx, etc.)
    - s3_key: Ruta en MinIO/S3
    - uploaded_by: FK a usuario que subió
    - expires_at: Expiración de URL pre-firmada
    """

    __tablename__ = "documents"

    entity_type = Column(Enum(EntityType), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # bytes
    mime_type = Column(String(100), nullable=True)
    
    # MinIO/S3 storage
    s3_key = Column(String(500), nullable=False, index=True)
    
    # Metadata
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    expires_at = Column(__import__('sqlalchemy').DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, file_name={self.file_name}, entity_type={self.entity_type})>"

    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Validate file size (max 50MB)."""
        MAX_SIZE = 52_428_800  # 50MB in bytes
        return 0 < file_size <= MAX_SIZE
