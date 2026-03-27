"""
Request/Response logging middleware
"""
import logging
import time
from uuid import uuid4
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and log details.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or endpoint
            
        Returns:
            HTTP response
        """
        request_id = str(uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        # Log request
        logger.info(
            f"Request [{request_id}] {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            },
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"Request [{request_id}] failed: {str(exc)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration": process_time,
                },
                exc_info=True,
            )
            raise

        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"Response [{request_id}] {response.status_code} ({process_time:.3f}s)",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": process_time,
            },
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
