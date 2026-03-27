"""
Custom Exceptions for PACTA Backend
"""
from typing import Any, Optional


class PACTAException(Exception):
    """Base exception for all PACTA errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class APIException(PACTAException):
    """General API exception."""

    def __init__(self, message: str, status_code: int = 400, code: str = "BAD_REQUEST"):
        super().__init__(message, code, status_code)


class ValidationException(PACTAException):
    """Raised when validation fails."""

    def __init__(self, message: str, field: Optional[str] = None, code: str = "VALIDATION_ERROR"):
        self.field = field
        super().__init__(message, code, 422)


class AuthException(PACTAException):
    """Raised for authentication errors."""

    def __init__(self, message: str = "Authentication failed", code: str = "AUTH_ERROR"):
        super().__init__(message, code, 401)


class AuthorizationException(PACTAException):
    """Raised for authorization errors."""

    def __init__(self, message: str = "Not authorized", code: str = "AUTHORIZATION_ERROR"):
        super().__init__(message, code, 403)


class NotFoundException(PACTAException):
    """Raised when resource is not found."""

    def __init__(self, resource: str, identifier: Any = None, code: str = "NOT_FOUND"):
        message = f"{resource} not found"
        if identifier:
            message += f" (ID: {identifier})"
        super().__init__(message, code, 404)


class ConflictException(PACTAException):
    """Raised when there is a conflict (e.g., duplicate)."""

    def __init__(self, message: str, code: str = "CONFLICT"):
        super().__init__(message, code, 409)


class DatabaseException(PACTAException):
    """Raised for database errors."""

    def __init__(self, message: str, code: str = "DATABASE_ERROR"):
        super().__init__(message, code, 500)


class RateLimitException(PACTAException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", code: str = "RATE_LIMIT_ERROR"):
        super().__init__(message, code, 429)
