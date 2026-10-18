.DEFAULT_GOAL := help
PORT ?= 8000
COMPOSE ?= docker compose
POSTGRES_DATABASES := lunch_roulette lunch_roulette_test

.PHONY: help dashboard-start db-start db-stop db-down db-reset db-crud-test migrate factory-install-python factory-test-postgresql factory-test factory-check factory-install-python-bootstrap factory-test-python factory-lint-python factory-format-check-python factory-type-syntax-check-python factory-full-check-python

help: ## Show all targets
	@awk 'BEGIN {FS = ":.*?## "; indent = "  "} \
		/^##@@/ {printf "  \033[2m%s\033[0m\n", substr($$0, 6); indent = "    "; next} \
		/^##@/ {printf "\n\033[1m%s\033[0m\n", substr($$0, 5); indent = "  "; next} \
		/^[a-zA-Z0-9_.-]+:.*?## / {printf "%s\033[36m%-24s\033[0m %s\n", indent, $$1, $$2}' $(MAKEFILE_LIST)

##@ Dashboard

dashboard-start: ## Start the factory dashboard as a background service
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

##@ Database

db-start: ## Start PostgreSQL and wait until it is healthy
	@$(COMPOSE) up -d --wait db

db-stop: ## Stop the local PostgreSQL service and preserve its data
	@$(COMPOSE) stop db

db-down: ## Remove the PostgreSQL container and network but preserve its data
	@$(COMPOSE) down

db-reset: ## DESTRUCTIVE: delete all local database data
	@$(COMPOSE) down -v

migrate: ## Apply pending migrations to the development and test databases
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

##@ Factory

##@@ PostgreSQL

factory-test-postgresql: db-start ## [local dev] Start PostgreSQL and run the product test suite
	uv run pytest

##@@ Isolation test

factory-test: ## [factory agents] Run the product test suite inside an isolated factory slot
	@test -n "$$LR_TEST_DATABASE_URL" || { echo "LR_TEST_DATABASE_URL is required" >&2; exit 2; }
	@test -n "$$FACTORY_TEST_SLOT" || { echo "FACTORY_TEST_SLOT is required" >&2; exit 2; }
	PYTHONDONTWRITEBYTECODE=1 COVERAGE_FILE=".coverage.$$FACTORY_TEST_SLOT" uv run pytest -o cache_dir=".pytest_cache/$$FACTORY_TEST_SLOT"

factory-check: ## [factory agents] Run lint, format, and type checks inside an isolated factory slot
	@test -n "$$FACTORY_TEST_SLOT" || { echo "FACTORY_TEST_SLOT is required" >&2; exit 2; }
	RUFF_CACHE_DIR=".ruff_cache/$$FACTORY_TEST_SLOT" uv run ruff check
	RUFF_CACHE_DIR=".ruff_cache/$$FACTORY_TEST_SLOT" uv run ruff format --check
	MYPY_CACHE_DIR=".mypy_cache/$$FACTORY_TEST_SLOT" uv run mypy

##@@ Python

factory-install-python: ## [local dev] Set up the Python environment and install dependencies
	uv sync

factory-install-python-bootstrap: ## [factory bootstrap] Placeholder for the factory's own install step (currently a no-op)
	:

factory-test-python: ## [factory bootstrap] Run the factory's own test suite
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'

factory-lint-python: ## [factory bootstrap] Check the factory's shell scripts for syntax errors
	sh -n factory/branch-guard.sh && sh -n factory/orchestrator-lock.sh && sh -n factory/slot.sh

factory-format-check-python: ## [factory bootstrap] Check the factory's generated files are up to date
	python3 factory/render-runtime-adapters.py --check

factory-type-syntax-check-python: ## [factory bootstrap] Check the factory's Python scripts for syntax errors
	python3 -c "import ast,pathlib; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8')) for p in ('factory/render-runtime-adapters.py','tests/test_factory_orchestration.py')]"

factory-full-check-python: ## [factory bootstrap] Run the factory's test, lint, and format checks together
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' && sh -n factory/branch-guard.sh && sh -n factory/orchestrator-lock.sh && sh -n factory/slot.sh && python3 factory/render-runtime-adapters.py --check
