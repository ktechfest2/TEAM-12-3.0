SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

.PHONY: help setup dev fmt lint typecheck test types build verify clean

help: ## List commands
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

setup: ## Install dependencies from the lockfile
	pnpm install --frozen-lockfile

dev: ## Vite dev server on :5173
	pnpm dev

fmt: ## Format and autofix
	pnpm fmt

lint: ## Lint and format check (no changes)
	pnpm lint

typecheck: ## TypeScript strict
	pnpm typecheck

test: ## Vitest
	pnpm test

types: ## Regenerate src/lib/api/schema.gen.ts from contracts/openapi.json
	pnpm types

build: ## Production build to dist/
	pnpm build

verify: lint typecheck test build ## Everything CI checks for the web app

clean:
	rm -rf dist coverage node_modules/.vite
