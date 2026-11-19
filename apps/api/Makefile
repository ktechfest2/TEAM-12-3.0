SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help
UV := uv run

.PHONY: help setup dev worker fmt lint typecheck test test-integration openapi db-migrate db-revision seed-sources verify clean

help: ## List commands
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

setup: ## Install dependencies from the lockfile
	uv sync --frozen

dev: ## Run the API with reload on :8000
	$(UV) uvicorn clarion_api.main:app --reload --port 8000

worker: ## Run the background worker
	$(UV) taskiq worker clarion_api.worker.broker:broker clarion_api.worker.tasks

fmt: ## Format and autofix
	$(UV) ruff format .
	$(UV) ruff check --fix .

lint: ## Lint and check formatting (no changes)
	$(UV) ruff check .
	$(UV) ruff format --check .

typecheck: ## mypy strict
	$(UV) mypy

test: ## Unit and API tests (integration tests skip unless RUN_INTEGRATION=1)
	APP_ENV=test $(UV) pytest

openapi: ## Write ../../contracts/openapi.json
	APP_ENV=test $(UV) python scripts/export_openapi.py ../../contracts/openapi.json

db-migrate: ## Apply migrations to DATABASE_URL
	$(UV) alembic upgrade head

seed-sources: ## Load official passages: make seed-sources FILE=passages.json
	@test -n "$(FILE)" || { echo "usage: make seed-sources FILE=passages.json" >&2; exit 2; }
	$(UV) python scripts/seed_sources.py "$(FILE)"

db-revision: ## New migration: make db-revision m="add x"
	$(UV) alembic revision --autogenerate -m "$(m)"

verify: lint typecheck test ## Everything CI checks for the API

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov var
