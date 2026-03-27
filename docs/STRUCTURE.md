# 📐 PACTA Backend — Estructura del Monorepo

**Versión:** 1.0  
**Fecha:** 2026-03-27  
**Estado:** Inicializada para Fase 1

---

## 📂 Directorios Principales

### `api/` — Servicio FastAPI + GraphQL Principal

```
api/
├── src/                    # Código fuente
│   ├── main.py            # Entry point, FastAPI app
│   ├── config.py          # Configuración, env vars
│   │
│   ├── schemas/           # Pydantic DTOs
│   │   ├── contract.py
│   │   ├── client.py
│   │   ├── supplier.py
│   │   ├── signatory.py
│   │   ├── supplement.py
│   │   ├── document.py
│   │   ├── user.py
│   │   ├── notification.py
│   │   ├── audit.py
│   │   └── common.py
│   │
│   ├── models/            # SQLAlchemy ORM models
│   │   ├── base.py        # BaseModel con UUID, timestamps
│   │   ├── contract.py
│   │   ├── client.py
│   │   ├── supplier.py
│   │   ├── signatory.py
│   │   ├── supplement.py
│   │   ├── document.py
│   │   ├── user.py
│   │   ├── notification.py
│   │   └── audit_log.py
│   │
│   ├── repositories/      # Data access layer
│   │   ├── base.py        # Generic CRUD BaseRepository<T>
│   │   ├── contract.py
│   │   ├── client.py
│   │   ├── supplier.py
│   │   ├── signatory.py
│   │   ├── supplement.py
│   │   ├── document.py
│   │   ├── user.py
│   │   └── notification.py
│   │
│   ├── services/          # Business logic layer
│   │   ├── auth.py        # JWT, login, refresh, password
│   │   ├── contract.py
│   │   ├── client.py
│   │   ├── supplier.py
│   │   ├── signatory.py
│   │   ├── supplement.py
│   │   ├── document.py
│   │   ├── user.py
│   │   ├── notification.py
│   │   ├── report.py      # Reportes (distribución, financiero, vencimientos)
│   │   └── audit.py       # Auto-logging
│   │
│   ├── api/               # API routes (REST)
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py        # POST /auth/login, /auth/refresh
│   │   │   │   ├── contracts.py   # GET/POST /contracts/*
│   │   │   │   ├── clients.py
│   │   │   │   ├── suppliers.py
│   │   │   │   ├── signatories.py
│   │   │   │   ├── supplements.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── users.py
│   │   │   │   ├── notifications.py
│   │   │   │   ├── reports.py
│   │   │   │   └── audit.py
│   │   │   └── router.py  # APIRouter raíz
│   │   └── deps.py        # Dependency injection
│   │
│   ├── graphql/           # GraphQL schema (Strawberry)
│   │   ├── types.py       # @strawberry types
│   │   ├── queries.py     # Query type
│   │   ├── mutations.py   # Mutation type
│   │   ├── subscriptions.py  # Subscription type (WebSocket)
│   │   └── schema.py      # Combined schema
│   │
│   ├── core/              # Core utilities & patterns
│   │   ├── security.py    # JWT, bcrypt, password validation
│   │   ├── exceptions.py  # Custom exceptions (APIException, etc.)
│   │   ├── logging.py     # Structured logging
│   │   └── enums.py       # ContractStatus, ContractType, etc.
│   │
│   ├── db/                # Database setup
│   │   ├── session.py     # AsyncSession factory
│   │   └── (migrations/)  # Alembic migrations
│   │
│   ├── storage/           # S3/MinIO integration
│   │   └── s3.py          # Upload, download, presigned URLs
│   │
│   ├── tasks/             # Background tasks
│   │   ├── contract_expiry.py
│   │   └── notifications.py
│   │
│   └── utils/             # Helpers
│       ├── validators.py
│       ├── formatters.py
│       └── helpers.py
│
├── tests/                 # Tests
│   ├── unit/              # Unit tests (mocks)
│   │   ├── test_auth.py
│   │   ├── test_contract_service.py
│   │   ├── test_client_service.py
│   │   ├── test_validators.py
│   │   └── ...
│   │
│   ├── integration/       # Integration tests (DB)
│   │   ├── test_auth_flow.py
│   │   ├── test_contract_crud.py
│   │   ├── test_graphql_queries.py
│   │   ├── test_notifications.py
│   │   └── ...
│   │
│   └── fixtures/
│       ├── db.py          # DB fixtures
│       └── users.py       # User/auth fixtures
│
├── migrations/            # Alembic
│   ├── env.py
│   ├── script.py_mako
│   └── versions/
│
├── pyproject.toml         # Dependencies
├── alembic.ini           # Migration config
├── pytest.ini            # Test config
└── .env.example
```

**Responsabilidades:**
- ✅ Exponer REST API endpoints
- ✅ Exponer GraphQL endpoint
- ✅ CRUD de entidades
- ✅ Autenticación y autorización
- ✅ Integración con BD (PostgreSQL)
- ✅ Almacenamiento de documentos (MinIO)

---

### `workers/` — Servicios Background

```
workers/
├── src/
│   ├── main.py            # Entry point, APScheduler
│   ├── config.py
│   │
│   ├── tasks/
│   │   ├── contract_expiry.py   # Cron diario 8am: busca vencimientos
│   │   └── notifications.py     # Cron diario 9am: reminders
│   │
│   └── utils/
│
├── tests/
│   ├── unit/               # Tests de tasks
│   └── integration/
│
└── pyproject.toml
```

**Responsabilidades:**
- ✅ Ejecutar tareas en background (APScheduler)
- ✅ Verificar vencimientos de contratos
- ✅ Crear notificaciones automáticas
- ✅ Reminder de suplementos pendientes

**Comunicación con API:**
- Lee datos de PostgreSQL
- Crea notificaciones en tabla `notifications`
- Usa Redis para estado compartido

---

### `shared/` — Código Compartido

```
shared/
├── src/
│   ├── schemas/           # DTOs comunes
│   │   ├── paginated.py   # PaginatedResponse
│   │   ├── pagination.py  # PaginationInput
│   │   └── errors.py      # ErrorResponse
│   │
│   ├── exceptions.py      # Excepciones personalizadas
│   │   ├── APIException
│   │   ├── AuthException
│   │   ├── ValidationException
│   │   └── ...
│   │
│   ├── enums.py           # Enumeraciones globales
│   │   ├── ContractStatus
│   │   ├── ContractType
│   │   ├── UserRole
│   │   └── ...
│   │
│   ├── security.py        # Seguridad compartida
│   │   ├── hash_password()
│   │   ├── verify_password()
│   │   ├── create_access_token()
│   │   └── decode_token()
│   │
│   ├── logging.py         # Logging estructurado
│   │   └── get_logger()
│   │
│   └── utils/
│       └── ...
│
└── tests/
```

**Responsabilidades:**
- ✅ Definir tipos, esquemas, excepciones compartidas
- ✅ Funciones de seguridad (JWT, hashing)
- ✅ Logging y utilidades comunes

**Uso:**
- `api/` importa de `shared/` para excepciones, enums, seguridad
- `workers/` importa de `shared/` para logging, enums

---

### `infra/` — Infraestructura

```
infra/
├── docker/
│   ├── Dockerfile.api      # Para el servicio API
│   ├── Dockerfile.workers  # Para los workers
│   └── docker-compose.yml  # (linked from root)
│
├── k8s/                     # Kubernetes manifests (future)
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ...
│
└── terraform/              # Infrastructure as Code (future)
    ├── main.tf
    └── ...
```

---

### `docs/` — Documentación del Backend

```
docs/
├── API.md                  # REST endpoints, ejemplos
├── GRAPHQL.md             # GraphQL schema, queries
├── ARCHITECTURE.md        # ADRs, patrones
├── DATABASE.md            # Schema, índices
├── TESTING.md             # Estrategia testing
└── DEPLOYMENT.md          # Guía deployment
```

---

### `scripts/` — Scripts Útiles

```
scripts/
├── setup-dev.sh           # Setup local dev
├── run-tests.sh           # Correr tests
├── lint.sh                # Lint + format
├── seed-db.sh             # Cargar datos de prueba
└── ...
```

---

## 🔄 Flujo de Datos

```
Cliente Web
    │
    ▼
┌─────────────────────────────────────┐
│   FastAPI (api/src/main.py)         │
│                                     │
│  ├─ REST endpoints (/api/v1/*)      │
│  ├─ GraphQL endpoint (/graphql)     │
│  ├─ OpenAPI docs (/docs)            │
│  └─ WebSocket (subscriptions)       │
└──────────┬──────────────────────────┘
           │
    ┌──────┼──────┐
    │      │      │
    ▼      ▼      ▼
 Services  Repos  Auth
    │      │      │
    └──────┼──────┘
           │
           ▼
    ┌──────────────────────┐
    │  PostgreSQL          │
    │  (Base de datos)     │
    └──────────────────────┘

Background Workers
    │
    ▼
┌──────────────────────────────┐
│ APScheduler (workers/)       │
│                              │
│ ├─ contract_expiry (8am)     │
│ ├─ notification_reminder (9am)
│ └─ ...                       │
└──────────┬──────────────────┘
           │
    ┌──────┼──────┐
    │      │      │
    ▼      ▼      ▼
  Tasks  Repos  Utils
    │      │      │
    └──────┼──────┘
           │
    ┌──────┴──────────┐
    │                 │
    ▼                 ▼
PostgreSQL        Redis (state)
```

---

## 🚀 Ciclo de Desarrollo

### 1. Implementación

1. Crear Pydantic schema en `api/src/schemas/`
2. Crear SQLAlchemy model en `api/src/models/`
3. Crear migration Alembic (`alembic revision --autogenerate`)
4. Crear repository en `api/src/repositories/`
5. Crear service en `api/src/services/`
6. Crear API endpoints en `api/src/api/v1/endpoints/`
7. Crear GraphQL types/queries/mutations
8. Escribir tests (unit + integration)

### 2. Testing

```bash
make test-unit          # Unit tests
make test-integration   # Integration tests
make test-coverage      # Con cobertura
```

### 3. Linting & Format

```bash
make format             # Black + Ruff fix
make lint               # Verificar linting
```

### 4. Database

```bash
make db-migrate        # Aplicar migraciones
```

---

## 📋 Fase 1 Checklist (Fundaciones)

- [ ] Proyecto inicializado (estructura)
- [ ] BD y ORM configurado
- [ ] Autenticación JWT implementada
- [ ] CRUD de usuarios funcional
- [ ] Repository pattern implementado
- [ ] Exception handling global
- [ ] Logging estructurado
- [ ] CI/CD setup (GitHub Actions)
- [ ] OpenAPI documentación
- [ ] Tests básicos corriendo

**Estado actual:** ✅ Estructura creada, lista para Phase 1 implementation

---

## 🔧 Próximos Pasos

1. Crear `pyproject.toml` en `api/`, `workers/`, `shared/`
2. Implementar `main.py` en `api/` y `workers/`
3. Crear modelos base en `api/src/models/base.py`
4. Configurar autenticación JWT
5. Crear usuarios CRUD
6. Iniciar tests

