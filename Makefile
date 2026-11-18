# Root task runner. Each app has its own Makefile; this one fans out.
SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

.PHONY: help setup dev fmt lint typecheck test contract verify services-up services-down db-migrate clean

help: ## List commands
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: ## Install all dependencies and git hooks
	$(MAKE) -C apps/api setup
	$(MAKE) -C apps/web setup
	uvx pre-commit install --install-hooks

dev: ## Run API, worker and web together
	./scripts/dev.sh

fmt: ## Format all code
	$(MAKE) -C apps/api fmt
	$(MAKE) -C apps/web fmt

lint: ## Lint all code
	$(MAKE) -C apps/api lint
	$(MAKE) -C apps/web lint

typecheck: ## Type check all code
	$(MAKE) -C apps/api typecheck
	$(MAKE) -C apps/web typecheck

test: ## Run all tests
	$(MAKE) -C apps/api test
	$(MAKE) -C apps/web test

contract: ## Export OpenAPI from the API and regenerate web types
	$(MAKE) -C apps/api openapi
	$(MAKE) -C apps/web types

verify: ## Full gate, identical to CI
	./scripts/verify.sh

services-up: ## Start Postgres (pgvector) and Redis locally
	docker compose -f infra/docker-compose.yml up -d

services-down: ## Stop local services
	docker compose -f infra/docker-compose.yml down

db-migrate: ## Apply database migrations
	$(MAKE) -C apps/api db-migrate

clean: ## Remove caches and build output
	$(MAKE) -C apps/api clean
	$(MAKE) -C apps/web clean
