# 🚀 PACTA Backend — Monorepo

**Versión:** 2.0  
**Fecha:** 2026-03-27  
**Stack:** FastAPI, PostgreSQL, GraphQL (Strawberry), Redis, MinIO

---

## 📂 Estructura Monorepo

Este es un **monorepo con worktree** que contiene múltiples servicios y módulos:

```
pacta-backend/
├── api/                          # Servicio principal FastAPI + GraphQL
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py              # Entry point
│   │   ├── config.py
│   │   ├── schemas/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── api/
│   │   ├── graphql/
│   │   ├── core/
│   │   ├── db/
│   │   ├── storage/
│   │   └── utils/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   ├── migrations/              # Alembic migrations
│   ├── pyproject.toml
│   ├── alembic.ini
│   └── .env.example
│
├── workers/                      # Servicios background (APScheduler, etc.)
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py              # Background job scheduler
│   │   ├── tasks/
│   │   │   ├── contract_expiry.py
│   │   │   ├── notifications.py
│   │   │   └── __init__.py
│   │   ├── config.py
│   │   └── utils/
│   ├── tests/
│   └── pyproject.toml
│
├── shared/                       # Código compartido entre servicios
│   ├── src/
│   │   ├── __init__.py
│   │   ├── schemas/             # Schemas reutilizables
│   │   ├── exceptions.py         # Excepciones comunes
│   │   ├── enums.py             # Enumeraciones globales
│   │   ├── security.py          # Seguridad, JWT, etc.
│   │   ├── logging.py           # Logging compartido
│   │   └── utils/
│   ├── tests/
│   └── pyproject.toml
│
├── infra/                        # Infraestructura, Docker, Kubernetes
│   ├── docker/
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.workers
│   │   └── docker-compose.yml   # Local development
│   ├── k8s/                      # Kubernetes manifests (future)
│   └── terraform/               # Infrastructure as Code (future)
│
├── docs/                         # Documentación del backend
│   ├── API.md                   # OpenAPI & REST endpoints
│   ├── GRAPHQL.md               # GraphQL schema
│   ├── ARCHITECTURE.md          # Decisiones arquitectónicas
│   ├── DATABASE.md              # Schema, migraciones
│   ├── TESTING.md               # Estrategia de testing
│   └── DEPLOYMENT.md            # Guía de deployment
│
├── scripts/                      # Scripts útiles
│   ├── setup-dev.sh
│   ├── run-tests.sh
│   ├── lint.sh
│   └── seed-db.sh
│
├── .gitignore
├── .env.example
├── docker-compose.yml           # Local development stack
├── pyproject.toml               # Root dependencies
├── Makefile                      # Tasks comunes
└── README.md                     # Este archivo
```

---

## 🎯 Componentes Principales

### 1️⃣ **api/** — FastAPI + GraphQL
El servicio principal que expone:
- ✅ REST API endpoints (`/api/v1/*`)
- ✅ GraphQL endpoint (`/graphql`)
- ✅ OpenAPI docs (`/docs`)
- ✅ CRUD de entidades (Contratos, Clientes, Proveedores, etc.)
- ✅ Autenticación JWT
- ✅ Autorización por roles

**Tecnologías:**
- FastAPI 0.115+
- SQLAlchemy 2.x async
- Pydantic v2
- Strawberry GraphQL
- asyncpg

### 2️⃣ **workers/** — Background Jobs
Servicios que corren en background:
- ✅ Verificación diaria de vencimientos (APScheduler)
- ✅ Reminders de suplementos pendientes
- ✅ Generación de notificaciones

**Tecnologías:**
- APScheduler
- Redis (para estado compartido)
- SQLAlchemy async

### 3️⃣ **shared/** — Código Compartido
Módulo reutilizable entre servicios:
- ✅ Schemas Pydantic comunes
- ✅ Excepciones personalizadas
- ✅ Enumeraciones (ContractStatus, ContractType, etc.)
- ✅ Seguridad (JWT, bcrypt)
- ✅ Logging estructurado

### 4️⃣ **infra/** — Infraestructura
Configuración de despliegue:
- ✅ Docker: `Dockerfile.api`, `Dockerfile.workers`
- ✅ docker-compose.yml para desarrollo local
- ✅ Kubernetes manifests (future)
- ✅ Terraform (future)

### 5️⃣ **docs/** — Documentación
Documentación del backend:
- ✅ API REST reference
- ✅ GraphQL schema documentation
- ✅ Decisiones arquitectónicas
- ✅ Schema de BD
- ✅ Estrategia de testing

---

## 🚀 Quick Start

### Requisitos
- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- Git

### 1. Setup inicial

```bash
# Clonar este monorepo
git clone <repo-url> pacta-backend
cd pacta-backend

# Crear virtual environment (en root)
python3.12 -m venv venv
source venv/bin/activate

# Instalar dependencias (root + servicios)
make install

# Copiar env vars
cp .env.example .env
# Editar .env con configuración local
```

### 2. Iniciar BD y servicios

```bash
# Levantar PostgreSQL, Redis, MinIO en Docker
docker-compose up -d

# Ejecutar migraciones
cd api && alembic upgrade head
```

### 3. Correr API

```bash
cd api
python -m uvicorn src.main:app --reload --port 8000
```

**API disponible en:** http://localhost:8000
- 📖 **Docs:** http://localhost:8000/docs
- 📖 **ReDoc:** http://localhost:8000/redoc
- 📈 **GraphQL:** http://localhost:8000/graphql

### 4. Correr Workers (en otra terminal)

```bash
cd workers
python -m src.main
```

### 5. Tests

```bash
# Tests unitarios
make test-unit

# Tests integración
make test-integration

# Cobertura
make test-coverage
```

---

## 📋 Fases de Implementación

Ver `/home/mowgli/pacta/pacta-docs/plans/BACKEND_IMPLEMENTATION_PLAN.md` para el plan completo.

### Fase 1: Fundaciones (15-18 días)
- Proyecto, BD, auth, usuarios, repository pattern, CI/CD

### Fase 2: Core Modules (14-17 días)
- Clients, Suppliers, Signatories, Contracts, Supplements

### Fase 3: Secondary Modules (18-21 días)
- Documents, Audit Logs, Notifications, Reports, GraphQL

### Fase 4: Testing & Production (18-22 días)
- Testing, performance, security, deployment

**Timeline total:** 65-78 días (~10-11 semanas)

---

## 🔧 Commands

```bash
# Setup
make install              # Instalar todas las dependencias
make setup-dev           # Setup development environment

# Development
make run-api             # Correr API en modo desarrollo
make run-workers         # Correr background jobs
make run-all             # Correr todo (api + workers)

# Testing
make test                # Correr todos los tests
make test-unit          # Solo unit tests
make test-integration   # Solo integration tests
make test-coverage      # Con cobertura
make lint               # Black + Ruff

# Database
make db-migrate         # Correr migraciones
make db-rollback        # Deshacer última migración
make db-seed            # Cargar datos de prueba

# Cleanup
make clean              # Limpiar artefactos
```

---

## 🗄️ Estructura de BD

Ver `/home/mowgli/pacta/pacta-docs/plans/DATABASE_SCHEMA_SUMMARY.md`

**Tablas principales:**
1. users
2. clients
3. suppliers
4. signatories
5. contracts (core)
6. supplements
7. documents
8. notifications
9. audit_logs

---

## 🔐 Seguridad

- ✅ JWT con RS256 (asymmetric) o HS256 (symmetric)
- ✅ Refresh tokens rotativos
- ✅ bcrypt para contraseñas (factor 12)
- ✅ Rate limiting en endpoints sensibles
- ✅ SQL injection prevention (ORM)
- ✅ CORS configurado
- ✅ Security headers

---

## 📚 Documentación Completa

| Archivo | Contenido |
|---------|----------|
| `docs/API.md` | REST endpoints, schemas, ejemplos |
| `docs/GRAPHQL.md` | GraphQL queries, mutations, subscriptions |
| `docs/ARCHITECTURE.md` | ADRs, patrones, decisiones |
| `docs/DATABASE.md` | Schema, índices, constraints |
| `docs/TESTING.md` | Unit, integration, E2E tests |
| `docs/DEPLOYMENT.md` | Docker, K8s, CI/CD |

---

## 📞 Contribuir

1. Fork este repo (si es privado, clonar directamente)
2. Crear branch: `git checkout -b feature/nombre`
3. Commits con mensaje descriptivo
4. Push y abrir Pull Request
5. CI/CD debe pasar (tests, linting, type checking)

---

## 📝 Notas

- Este es un **monorepo** — múltiples servicios en un repo
- Cada servicio (api, workers) tiene su `pyproject.toml` independiente
- Código compartido en `shared/`
- Tests en `tests/` de cada servicio
- Documentación centralizada en `docs/`

---

**Generado:** 2026-03-27  
**Versión:** 1.0  
**Estado:** Ready for Phase 1 implementation
