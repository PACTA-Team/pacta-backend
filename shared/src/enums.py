"""
Enumerations for PACTA Backend
"""
from enum import Enum


class UserRole(str, Enum):
    """User roles."""

    ADMIN = "admin"
    MANAGER = "manager"
    EDITOR = "editor"
    VIEWER = "viewer"


class ContractStatus(str, Enum):
    """Contract status."""

    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    TERMINATED = "terminated"


class ContractType(str, Enum):
    """Contract types."""

    SERVICE = "service"
    SUPPLY = "supply"
    LICENSE = "license"
    LEASING = "leasing"
    MAINTENANCE = "maintenance"
    CONSULTING = "consulting"
    PARTNERSHIP = "partnership"
    OTHER = "other"


class SupplementStatus(str, Enum):
    """Supplement status."""

    DRAFT = "draft"
    APPROVED = "approved"
    ACTIVE = "active"
    CANCELLED = "cancelled"


class NotificationType(str, Enum):
    """Notification types."""

    CONTRACT_EXPIRING = "contract_expiring"
    SUPPLEMENT_PENDING = "supplement_pending"
    STATUS_CHANGED = "status_changed"
    DOCUMENT_UPLOADED = "document_uploaded"


class AuditAction(str, Enum):
    """Audit log actions."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class IdentityType(str, Enum):
    """Identity document types."""

    DNI = "dni"
    PASSPORT = "passport"
    RUT = "rut"
    OTHER = "other"


class EntityType(str, Enum):
    """Entity types for polymorphic relationships."""

    CONTRACT = "contract"
    CLIENT = "client"
    SUPPLIER = "supplier"
    SUPPLEMENT = "supplement"
