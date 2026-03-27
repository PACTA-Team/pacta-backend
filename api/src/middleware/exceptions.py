"""
Global exception handlers and middleware for FastAPI
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import logging
import traceback
from uuid import uuid4

from shared.src.exceptions import (
    PACTAException,
    ValidationException,
    AuthException,
    NotFoundException,
    ConflictException,
    RateLimitException,
)

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Structured error response."""

    def __init__(
        self,
        error_id: str,
        status_code: int,
        message: str,
        details: dict = None,
        path: str = None,
    ):
        self.error_id = error_id
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        self.path = path

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "error_id": self.error_id,
            "status_code": self.status_code,
            "message": self.message,
            "details": self.details,
            "path": self.path,
        }


def register_exception_handlers(app: FastAPI):
    """
    Register all global exception handlers.
    
    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request: Request, exc: ValidationException):
        """Handle validation exceptions."""
        error_id = str(uuid4())
        logger.warning(f"Validation error [{error_id}]: {exc.message}", extra={"error_id": error_id})

        error_response = ErrorResponse(
            error_id=error_id,
            status_code=status.HTTP_400_BAD_REQUEST,
            message=exc.message,
            details=exc.details,
            path=str(request.url.path),
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(error_response.to_dict()),
        )

    @app.exception_handler(AuthException)
    async def auth_exception_handler(request: Request, exc: AuthException):
        """Handle authentication exceptions."""
        error_id = str(uuid4())
        logger.warning(f"Auth error [{error_id}]: {exc.message}", extra={"error_id": error_id})

        error_response = ErrorResponse(
            error_id=error_id,
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=exc.message,
            path=str(request.url.path),
        )

        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(error_response.to_dict()),
        )

    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException):
        """Handle not found exceptions."""
        error_id = str(uuid4())
        logger.warning(f"Not found error [{error_id}]: {exc.message}", extra={"error_id": error_id})

        error_response = ErrorResponse(
            error_id=error_id,
            status_code=status.HTTP_404_NOT_FOUND,
            message=exc.message,
            path=str(request.url.path),
        )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(error_response.to_dict()),
        )

    @app.exception_handler(ConflictException)
    async def conflict_exception_handler(request: Request, exc: ConflictException):
        """Handle conflict exceptions."""
        error_id = str(uuid4())
        logger.warning(f"Conflict error [{error_id}]: {exc.message}", extra={"error_id": error_id})

        error_response = ErrorResponse(
            error_id=error_id,
            status_code=status.HTTP_409_CONFLICT,
            message=exc.message,
            details=exc.details,
            path=str(request.url.path),
        )

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(error_response.to_dict()),
        )

    @app.exception_handler(RateLimitException)
    async def rate_limit_exception_handler(request: Request, exc: RateLimitException):
        """Handle rate limit exceptions."""
        error_id = str(uuid4())
        logger.warning(f"Rate limit error [{error_id}]: {exc.message}", extra={"error_id": error_id})

        error_response = ErrorResponse(
            error_id=error_id,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=exc.message,
            details={"retry_after": exc.details.get("retry_after") if exc.details else None},
            path=str(request.url.path),
        )

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=jsonable_encoder(error_response.to_dict()),
            headers={"Retry-After": str(exc.details.get("retry_after", 60)) if exc.details else "60"},
        )

    @app.exception_handler(PACTAException)
    async def pacta_exception_handler(request: Request, exc: PACTAException):
        """Handle generic PACTA exceptions."""
        error_id = str(uuid4())
        logger.error(f"PACTA error [{error_id}]: {exc.message}", extra={"error_id": error_id})

        error_response = ErrorResponse(
            error_id=error_id,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=exc.message,
            details=exc.details,
            path=str(request.url.path),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(error_response.to_dict()),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions."""
        error_id = str(uuid4())
        logger.error(
            f"Unhandled exception [{error_id}]: {str(exc)}",
            extra={"error_id": error_id, "traceback": traceback.format_exc()},
            exc_info=True,
        )

        error_response = ErrorResponse(
            error_id=error_id,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
            details={"original_error": type(exc).__name__},
            path=str(request.url.path),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(error_response.to_dict()),
        )
