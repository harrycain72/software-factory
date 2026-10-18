.DEFAULT_GOAL := help
PORT ?= 8000
COMPOSE ?= docker compose
POSTGRES_DATABASES := lunch_roulette lunch_roulette_test

.PHONY: help dashboard-start db-start db-stop db-down db-reset db-crud-test migrate install test check factory-test factory-check

help: ## Show all targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

dashboard-start: ## Start the factory dashboard as a background service (PORT=8000 by default)
	@pids=$$(lsof -ti tcp:$(PORT) -sTCP:LISTEN); \
	if [ -n "$$pids" ]; then \
		echo "Port $(PORT) is already in use; stopping the running service..."; \
		kill $$pids; \
		while lsof -ti tcp:$(PORT) -sTCP:LISTEN >/dev/null 2>&1; do sleep 0.2; done; \
	fi; \
	mkdir -p .factory-tmp; \
	nohup python3 -m http.server $(PORT) --bind 127.0.0.1 >.factory-tmp/dashboard.log 2>&1 & \
	echo $$! >.factory-tmp/dashboard.pid; \
	sleep 0.3; \
	echo "Dashboard: http://localhost:$(PORT)/platform/factory/dashboard.html (pid $$(cat .factory-tmp/dashboard.pid))"

db-start: ## Start PostgreSQL and wait until it is healthy
	@$(COMPOSE) up -d --wait db

db-stop: ## Stop the local PostgreSQL service and preserve its data
	@$(COMPOSE) stop db

db-down: ## Remove the PostgreSQL container and network but preserve its data
	@$(COMPOSE) down

db-reset: ## DESTRUCTIVE: removes the container and pgdata volume and deletes all local database data
	@$(COMPOSE) down -v

migrate: ## Run alembic upgrade head on the development and test databases
	@echo "Migrating the development database..."
	@uv run alembic upgrade head
	@echo "Migrating the test database..."
	@test_url="$${LR_TEST_DATABASE_URL:-$$(uv run python -c 'from lunch_roulette.settings import Settings; print(Settings().test_database_url)')}"; \
	uv run alembic -x database_url="$$test_url" upgrade head

db-crud-test: db-start ## Verify create, read, update, and delete in both local databases
	@set -e; \
	for database in $(POSTGRES_DATABASES); do \
		echo "Testing CRUD in $$database..."; \
		$(COMPOSE) exec -T db psql -X --set=ON_ERROR_STOP=1 -U postgres -d "$$database" \
			-c 'CREATE TEMPORARY TABLE make_crud_check (id integer PRIMARY KEY, value text NOT NULL);' \
			-c "INSERT INTO make_crud_check (id, value) VALUES (1, 'created');" \
			-c "SELECT 1 / CASE WHEN (SELECT value FROM make_crud_check WHERE id = 1) = 'created' THEN 1 ELSE 0 END;" \
			-c "UPDATE make_crud_check SET value = 'updated' WHERE id = 1;" \
			-c "SELECT 1 / CASE WHEN (SELECT value FROM make_crud_check WHERE id = 1) = 'updated' THEN 1 ELSE 0 END;" \
			-c "DELETE FROM make_crud_check WHERE id = 1;" \
			-c "SELECT 1 / CASE WHEN NOT EXISTS (SELECT 1 FROM make_crud_check) THEN 1 ELSE 0 END;"; \
	done; \
	echo "PostgreSQL CRUD checks passed."

install: ## Create the Python 3.12 environment and install locked dependencies (uv sync)
	uv sync

test: db-start ## Start PostgreSQL, then run the test suite with branch coverage
	uv run pytest

check: ## Lint, check formatting and type-check (ruff, mypy)
	uv run ruff check
	uv run ruff format --check
	uv run mypy

factory-test: ## Run tests in an isolated factory slot (requires LR_TEST_DATABASE_URL and FACTORY_TEST_SLOT)
	@test -n "$$LR_TEST_DATABASE_URL" || { echo "LR_TEST_DATABASE_URL is required" >&2; exit 2; }
	@test -n "$$FACTORY_TEST_SLOT" || { echo "FACTORY_TEST_SLOT is required" >&2; exit 2; }
	PYTHONDONTWRITEBYTECODE=1 COVERAGE_FILE=".coverage.$$FACTORY_TEST_SLOT" uv run pytest -o cache_dir=".pytest_cache/$$FACTORY_TEST_SLOT"

factory-check: ## Run checks with isolated factory caches (requires FACTORY_TEST_SLOT)
	@test -n "$$FACTORY_TEST_SLOT" || { echo "FACTORY_TEST_SLOT is required" >&2; exit 2; }
	RUFF_CACHE_DIR=".ruff_cache/$$FACTORY_TEST_SLOT" uv run ruff check
	RUFF_CACHE_DIR=".ruff_cache/$$FACTORY_TEST_SLOT" uv run ruff format --check
	MYPY_CACHE_DIR=".mypy_cache/$$FACTORY_TEST_SLOT" uv run mypy
