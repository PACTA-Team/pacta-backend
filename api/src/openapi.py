"""
OpenAPI/Swagger schema customization
"""
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI


def custom_openapi(app: FastAPI):
    """
    Customize OpenAPI schema with custom branding and grouping.
    
    Args:
        app: FastAPI application instance
    """
    if app.openapi_schema:
        return app.openapi_schema

    output = get_openapi(
        title="PACTA Backend API",
        version="1.0.0",
        description="""
# Contract Lifecycle Management (CLM) SaaS API

PACTA is a production Contract Lifecycle Management system designed for enterprise-grade 
contract management, negotiation, execution, and compliance.

## Core Features

- **Authentication & Authorization**: JWT-based security with role-based access control
- **Contract Management**: Full lifecycle from drafting to execution and renewal
- **Multi-party Workflows**: Support for clients, suppliers, and authorized signatories
- **Document Management**: File storage with S3/MinIO integration
- **Audit Trail**: Complete event logging for compliance
- **Notifications**: Real-time system and user notifications
- **Background Jobs**: Scheduled tasks and asynchronous processing

## Getting Started

1. **Authentication**: Use `/api/v1/auth/login` with email/password to get tokens
2. **Create Users**: Use `/api/v1/users` to manage system users
3. **Manage Contracts**: Use `/api/v1/contracts` for full contract lifecycle

## API Versioning

This API follows semantic versioning. The current version is `v1`.
Breaking changes will increment the major version number.

## Error Handling

All errors follow a consistent format with:
- `error_id`: Unique identifier for tracking/debugging
- `status_code`: HTTP status code
- `message`: Human-readable error message
- `details`: Additional context when available

## Rate Limiting

Rate limits are enforced per endpoint and returned via headers:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets
        """,
        routes=app.routes,
        tags=[
            {
                "name": "auth",
                "description": "Authentication & JWT token management",
            },
            {
                "name": "users",
                "description": "User management (CRUD)",
            },
            {
                "name": "clients",
                "description": "Client/company management",
            },
            {
                "name": "suppliers",
                "description": "Supplier/vendor management",
            },
            {
                "name": "signatories",
                "description": "Authorized signers management",
            },
            {
                "name": "contracts",
                "description": "Contract lifecycle management",
            },
            {
                "name": "supplements",
                "description": "Contract amendments & modifications",
            },
            {
                "name": "documents",
                "description": "Document storage & retrieval",
            },
            {
                "name": "notifications",
                "description": "System notifications",
            },
            {
                "name": "audit",
                "description": "Audit logs & compliance",
            },
            {
                "name": "reports",
                "description": "Reporting & analytics",
            },
            {
                "name": "health",
                "description": "System health & status",
            },
        ],
    )

    # Add security schemes
    output["components"] = {
        "schemas": {
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error_id": {"type": "string", "description": "Unique error identifier"},
                    "status_code": {"type": "integer", "description": "HTTP status code"},
                    "message": {"type": "string", "description": "Error message"},
                    "details": {"type": "object", "description": "Additional error details"},
                    "path": {"type": "string", "description": "Request path"},
                },
                "required": ["error_id", "status_code", "message"],
            }
        },
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT access token from /auth/login",
            }
        },
    }

    # Apply security to protected endpoints
    if "paths" in output:
        protected_paths = [
            "/api/v1/users",
            "/api/v1/clients",
            "/api/v1/suppliers",
            "/api/v1/contracts",
        ]
        for path, path_item in output["paths"].items():
            if any(protected_path in path for protected_path in protected_paths):
                for operation in ["get", "post", "put", "patch", "delete"]:
                    if operation in path_item:
                        if "security" not in path_item[operation]:
                            path_item[operation]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = output
    return app.openapi_schema
