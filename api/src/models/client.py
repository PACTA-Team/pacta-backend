"""
Client ORM model - Empresas cliente
"""
from sqlalchemy import Column, String, Boolean
from src.models.base import BaseModel


class Client(BaseModel):
    """
    Empresa cliente.
    
    Campos:
    - name: Nombre empresa - índice
    - address: Dirección
    - city: Ciudad
    - country: País
    - fiscal_code: Código fiscal (RUT/CUIT/NIF) - único, índice
    - phone: Teléfono
    - email: Email
    - contact_person: Persona de contacto
    - is_active: Empresa activa - índice
    """

    __tablename__ = "clients"

    name = Column(String(255), nullable=False, index=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    fiscal_code = Column(String(50), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    contact_person = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name={self.name}, fiscal_code={self.fiscal_code})>"
