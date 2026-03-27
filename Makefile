.PHONY: install setup-dev run-api run-workers run-all test test-unit test-integration test-coverage lint clean db-migrate db-rollback db-seed help

# Variables
PYTHON := python3.12
VENV := venv
API_DIR := api
WORKERS_DIR := workers
SHARED_DIR := shared

help:
	@echo "PACTA Backend Monorepo — Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install all dependencies"
	@echo "  make setup-dev     - Setup development environment"
	@echo ""
	@echo "Development:"
	@echo "  make run-api       - Run API server (port 8000)"
	@echo "  make run-workers   - Run background jobs"
	@echo "  make run-all       - Run API + Workers"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-coverage - Run tests with coverage report"
	@echo "  make lint          - Run Black + Ruff linting"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate    - Run pending migrations"
	@echo "  make db-rollback   - Rollback last migration"
	@echo "  make db-seed       - Seed test data"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Remove build artifacts and cache"

# Setup targets
install:
	@echo "📦 Installing dependencies..."
	$(PYTHON) -m pip install --upgrade pip poetry
	poetry install
	cd $(API_DIR) && poetry install
	cd $(WORKERS_DIR) && poetry install
	cd $(SHARED_DIR) && poetry install
	@echo "✅ Dependencies installed"

setup-dev: install
	@echo "🔧 Setting up development environment..."
	cp .env.example .env
	@echo "⚠️  Please update .env with your local configuration"
	docker-compose up -d
	@echo "✅ Development environment ready"
	@echo "   - PostgreSQL: localhost:5432"
	@echo "   - Redis: localhost:6379"
	@echo "   - MinIO: localhost:9000"

# Development targets
run-api:
	@echo "🚀 Starting API server..."
	cd $(API_DIR) && python -m uvicorn src.main:app --reload --port 8000

run-workers:
	@echo "⚙️  Starting background jobs..."
	cd $(WORKERS_DIR) && python -m src.main

run-all:
	@echo "🚀 Starting all services..."
	@echo "   Run 'make run-api' in another terminal"
	make run-workers

# Testing targets
test:
	@echo "🧪 Running all tests..."
	cd $(API_DIR) && pytest tests/ -v
	@echo "✅ All tests passed"

test-unit:
	@echo "🧪 Running unit tests..."
	cd $(API_DIR) && pytest tests/unit/ -v

test-integration:
	@echo "🧪 Running integration tests..."
	cd $(API_DIR) && pytest tests/integration/ -v

test-coverage:
	@echo "📊 Running tests with coverage..."
	cd $(API_DIR) && pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "📈 Coverage report: $(API_DIR)/htmlcov/index.html"

lint:
	@echo "🔍 Linting code..."
	cd $(API_DIR) && ruff check src/ tests/
	cd $(WORKERS_DIR) && ruff check src/ tests/
	cd $(SHARED_DIR) && ruff check src/ tests/
	@echo "✅ Linting passed"

type-check:
	@echo "🔍 Type checking..."
	mypy $(API_DIR)/src $(SHARED_DIR)/src --ignore-missing-imports
	@echo "✅ Type checking passed"

format:
	@echo "🎨 Formatting code..."
	cd $(API_DIR) && ruff format src/ tests/
	cd $(WORKERS_DIR) && ruff format src/ tests/
	cd $(SHARED_DIR) && ruff format src/ tests/
	@echo "✅ Formatting complete"

# Database targets
db-migrate:
	@echo "📦 Running migrations..."
	cd $(API_DIR) && alembic upgrade head
	@echo "✅ Migrations applied"

db-rollback:
	@echo "↩️  Rolling back last migration..."
	cd $(API_DIR) && alembic downgrade -1
	@echo "✅ Rollback complete"

db-seed:
	@echo "🌱 Seeding test data..."
	cd $(API_DIR) && python scripts/seed_db.py
	@echo "✅ Database seeded"

db-reset:
	@echo "⚠️  WARNING: This will drop all data!"
	@read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		cd $(API_DIR) && alembic downgrade base; \
		cd $(API_DIR) && alembic upgrade head; \
		make db-seed; \
		echo "✅ Database reset complete"; \
	else \
		echo "Cancelled"; \
	fi

# Cleanup targets
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf build/ dist/ *.egg-info htmlcov/
	@echo "✅ Cleanup complete"

# Docker targets
docker-up:
	@echo "🐳 Starting Docker containers..."
	docker-compose up -d
	@echo "✅ Containers started"

docker-down:
	@echo "🛑 Stopping Docker containers..."
	docker-compose down
	@echo "✅ Containers stopped"

docker-logs:
	docker-compose logs -f

# Utility targets
status:
	@echo "📊 Service Status:"
	@docker-compose ps || echo "Docker not running"
	@echo ""
	@echo "Python environment:"
	@which python3.12
	@python3.12 --version
