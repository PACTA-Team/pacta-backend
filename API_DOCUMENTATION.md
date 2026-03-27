# PACTA Backend API Documentation

## Endpoints Overview

All API endpoints are prefixed with `/api/v1`.

### Authentication (`/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/login` | Login with email/password, get JWT tokens |
| `POST` | `/auth/refresh` | Refresh access token using refresh token |
| `POST` | `/auth/logout` | Logout (invalidate token) |

**Example Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePassword123!"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Users (`/users`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users` | Create a new user |
| `GET` | `/users` | List all users (paginated) |
| `GET` | `/users/{id}` | Get user by ID |
| `PATCH` | `/users/{id}` | Update user (email, role) |
| `PATCH` | `/users/{id}/deactivate` | Deactivate user (soft delete) |
| `DELETE` | `/users/{id}` | Delete user (hard delete) |

**Create User:**
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePassword123!",
    "role": "USER"
  }'
```

**List Users with Pagination:**
```bash
curl -X GET 'http://localhost:8000/api/v1/users?skip=0&limit=10' \
  -H "Authorization: Bearer {access_token}"
```

## Authentication

All protected endpoints require a Bearer token in the `Authorization` header:

```bash
curl -X GET http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer {access_token}"
```

## Error Responses

All errors follow a consistent format:

```json
{
  "error_id": "550e8400-e29b-41d4-a716-446655440000",
  "status_code": 400,
  "message": "Validation error",
  "details": {
    "field": "email",
    "reason": "Invalid email format"
  },
  "path": "/api/v1/users"
}
```

### Common Error Codes

| Status | Meaning | Example |
|--------|---------|---------|
| `400` | Bad Request | Invalid input data |
| `401` | Unauthorized | Invalid/expired token |
| `404` | Not Found | Resource doesn't exist |
| `409` | Conflict | Duplicate email, resource already exists |
| `429` | Rate Limited | Too many requests |
| `500` | Server Error | Unhandled exception |

## Interactive API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Rate Limiting

Rate limits are applied per endpoint. Check response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704067200
```

If rate limited (429), retry after the `Retry-After` header.

## Development

### Running Locally

```bash
# Install dependencies
make install

# Start API server
make run-api

# Run tests
make test

# Check API at http://localhost:8000/docs
```

### Making Requests

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# 2. Use token in requests
curl -X GET http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN"
```

## API Design Principles

1. **Stateless**: Each request is independent, no session state
2. **RESTful**: Follows REST conventions for resource manipulation
3. **Predictable**: Consistent naming, structure, and error handling
4. **Secure**: JWT authentication, HTTPS in production
5. **Documented**: OpenAPI/Swagger for auto-generated documentation
6. **Versioned**: `/api/v1/` allows future breaking changes

## Upcoming Endpoints

Phase 2 will add:
- `/clients` - Client/company management
- `/suppliers` - Supplier/vendor management
- `/contracts` - Full contract lifecycle
- `/signatories` - Authorized signers management
- `/supplements` - Contract amendments

Phase 3 will add:
- `/documents` - File storage
- `/notifications` - System notifications
- `/audit` - Audit logs
- `/reports` - Analytics & reporting

See `/pacta-docs/plans/` for full implementation roadmap.
