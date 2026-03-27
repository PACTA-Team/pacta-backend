"""
PACTA Backend — FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.config import settings


# Lifecycle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown events.
    """
    # Startup
    print("🚀 Starting PACTA Backend...")
    # TODO: Initialize database connections, cache, etc.
    yield
    # Shutdown
    print("🛑 Shutting down PACTA Backend...")
    # TODO: Clean up connections


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Middleware: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Middleware: Trusted Host
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"],
)

# Middleware: Logging
app.add_middleware(LoggingMiddleware)

# Register exception handlers
register_exception_handlers(app)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to PACTA Backend",
        "version": settings.app_version,
        "docs": "/docs",
        "graphql": "/graphql",
    }


# Include API routers
from src.api.v1 import router as api_router
app.include_router(api_router)

# Customize OpenAPI schema
app.openapi = lambda: custom_openapi(app)

# TODO: Include GraphQL
# from src.graphql.schema import schema
# app.include_router(GraphQLRouter(schema, path="/graphql"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
