# jadecli-team-agents-sdk Makefile
# Single entry point for all dev, build, test, db, and deploy operations.
#
# Usage:
#   make install      — Install Python + Node dependencies
#   make test         — Run all tests
#   make dev          — Start Next.js dev server
#   make build        — Build for production
#   make deploy       — Deploy to Vercel
#   make db-branch    — Create Neon branch for safe migrations
#   make db-migrate   — Run migration on current Neon branch
#   make db-promote   — Apply migration to main branch
#   make setup        — First-time setup (CLIs, auth, env)
#   make claude-sync   — Sync Claude OAuth tokens to GitHub secrets
#   make help         — Show all targets

SHELL := /bin/bash
.DEFAULT_GOAL := help
.PHONY: help install install-py install-node test lint build dev deploy \
        setup setup-auth setup-env claude-sync apps-setup \
        db-branch db-migrate db-promote db-diff db-seed db-reset db-status \
        codegen clean

# ── Config ────────────────────────────────────────────────────────────
PROJECT_DIR := $(shell pwd)
VENV := $(PROJECT_DIR)/.venv
PY := $(VENV)/bin/python
UV := uv
NPX := npx
PYTEST := $(VENV)/bin/pytest
ALEMBIC := $(VENV)/bin/alembic
NEON := $(NPX) neonctl
VERCEL := $(NPX) vercel

# Neon branch name defaults to git branch or "dev"
NEON_BRANCH ?= $(shell git branch --show-current 2>/dev/null || echo dev)

# ── Help ──────────────────────────────────────────────────────────────
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ── Setup (first-time) ───────────────────────────────────────────────
setup: install setup-auth setup-env ## First-time project setup (install + auth + env)
	@echo "✓ Setup complete. Run 'make db-status' to verify Neon connection."

setup-auth: ## Authenticate Neon + Vercel CLIs (opens browser)
	@echo "→ Authenticating Neon CLI..."
	$(NEON) auth || true
	@echo "→ Authenticating Vercel CLI..."
	$(VERCEL) login || true
	@echo "→ Verifying auth..."
	$(NEON) me --output json 2>/dev/null && echo "  Neon: ✓" || echo "  Neon: ✗ run 'make setup-auth' again"
	$(VERCEL) whoami 2>/dev/null && echo "  Vercel: ✓" || echo "  Vercel: ✗ run 'make setup-auth' again"

setup-env: ## Pull env vars from Vercel + generate .env
	@if [ ! -f .env ]; then \
		echo "→ Creating .env from env.template..."; \
		grep -v '^#' env.template | grep '=' > .env; \
		echo "→ Pulling Vercel env vars..."; \
		$(VERCEL) env pull .env.vercel 2>/dev/null || true; \
		if [ -f .env.vercel ]; then \
			echo "  Merging Vercel vars into .env..."; \
			cat .env.vercel >> .env; \
			rm .env.vercel; \
		fi; \
		echo "✓ .env created. Fill in any missing values."; \
	else \
		echo "  .env already exists. To refresh: rm .env && make setup-env"; \
	fi

# ── Claude OAuth ──────────────────────────────────────────────────────
GITHUB_REPO ?= jadecli-ai/team-agents-sdk

claude-sync: ## Sync Claude OAuth tokens to GitHub repo secrets
	@./scripts/sync-claude-oauth.sh $(GITHUB_REPO)

# ── GitHub Apps Setup ────────────────────────────────────────────────
APPS_DIR := scripts/installations

apps-setup: ## Run all GitHub App installation scripts (config files + workflows)
	@echo "=== Running GitHub App setup scripts ==="
	@for script in $(APPS_DIR)/*.sh; do \
		echo ""; \
		bash "$$script"; \
	done
	@echo ""
	@echo "✓ All app configs generated. Commit and push to activate."

# ── Install ───────────────────────────────────────────────────────────
install: install-py install-node ## Install all dependencies

install-py: ## Install Python deps with uv
	$(UV) venv $(VENV) 2>/dev/null || true
	$(UV) pip install -e ".[dev]"
	@echo "✓ Python deps installed"

install-node: ## Install Node deps
	npm install
	@echo "✓ Node deps installed"

# ── Code Quality ──────────────────────────────────────────────────────
test: ## Run all tests
	$(PYTEST) tests/ -v --tb=short

lint: ## Lint Python with ruff
	$(VENV)/bin/ruff check src/ tests/ scripts/
	$(VENV)/bin/ruff format --check src/ tests/ scripts/

format: ## Auto-format Python
	$(VENV)/bin/ruff check --fix src/ tests/ scripts/
	$(VENV)/bin/ruff format src/ tests/ scripts/

codegen: ## Generate Drizzle schema from semantic YAML
	$(PY) scripts/codegen.py
	@echo "✓ Codegen complete"

codegen-check: ## Validate semantic YAML (no writes)
	$(PY) scripts/codegen.py --check

# ── Build & Dev ───────────────────────────────────────────────────────
build: ## Build Next.js for production
	npm run build

dev: ## Start Next.js dev server (Turbopack)
	npm run dev

# ── Database: Neon Branching Workflow ─────────────────────────────────
#
# Safe migration workflow:
#   1. make db-branch          Create a Neon branch (named after git branch)
#   2. make db-migrate         Run Alembic migration on the branch
#   3. make test               Run tests against the branch
#   4. make db-diff            Compare branch schema vs main
#   5. make db-promote         Run same migration on main branch
#   6. make db-branch-delete   Clean up the branch

db-status: ## Show Neon project info and branches
	@echo "→ Neon branches:"
	$(NEON) branches list --output json 2>/dev/null | $(PY) -m json.tool 2>/dev/null || \
		echo "  Could not list branches. Check NEON auth: make setup-auth"
	@echo ""
	@echo "→ Env check:"
	@$(PY) -c "from src.get_env import env; env.check()" 2>/dev/null || \
		echo "  Could not check env. Run: make install-py"

db-branch: ## Create Neon branch from main (name = git branch)
	@echo "→ Creating Neon branch: $(NEON_BRANCH)"
	$(NEON) branches create --name $(NEON_BRANCH) --output json
	@echo ""
	@echo "→ Getting connection string for branch..."
	$(NEON) connection-string $(NEON_BRANCH) --output json
	@echo ""
	@echo "✓ Branch '$(NEON_BRANCH)' created."
	@echo "  Update PRJ_NEON_DATABASE_URL in .env to point to this branch for testing."

db-migrate: ## Run Alembic migration (on current PRJ_NEON_DATABASE_URL)
	$(ALEMBIC) upgrade head
	@echo "✓ Migration complete"

db-migrate-gen: ## Auto-generate Alembic migration from model changes
	$(ALEMBIC) revision --autogenerate -m "$(or $(MSG),auto migration)"
	@echo "✓ Migration file generated in src/db/alembic/versions/"

db-migrate-sql: ## Apply raw SQL migration (0001_initial.sql)
	@echo "→ Applying migrations/0001_initial.sql..."
	$(PY) -c "\
import asyncio, asyncpg; \
from src.get_env import env; \
from pathlib import Path; \
sql = Path('migrations/0001_initial.sql').read_text(); \
url = env('PRJ_NEON_DATABASE_URL').replace('+asyncpg', '').replace('postgresql+asyncpg', 'postgresql'); \
async def run(): \
    conn = await asyncpg.connect(url.replace('postgresql+asyncpg://', 'postgresql://')); \
    await conn.execute(sql); \
    await conn.close(); \
    print('✓ SQL migration applied'); \
asyncio.run(run())"

db-diff: ## Compare schema between Neon branches
	@echo "→ Schema diff: main ↔ $(NEON_BRANCH)"
	$(NEON) branches schema-diff main $(NEON_BRANCH) 2>/dev/null || \
		echo "  schema-diff requires neonctl >= 2.x"

db-seed: ## Seed sample data
	$(PY) scripts/seed_db.py

db-branch-delete: ## Delete the current Neon branch
	@echo "→ Deleting Neon branch: $(NEON_BRANCH)"
	$(NEON) branches delete $(NEON_BRANCH) --output json

db-reset: ## Reset branch to parent state (DESTRUCTIVE)
	@echo "⚠ Resetting branch '$(NEON_BRANCH)' to parent state..."
	@read -p "  Continue? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	$(NEON) branches reset $(NEON_BRANCH)

# ── Deploy ────────────────────────────────────────────────────────────
deploy: build ## Deploy to Vercel (production)
	$(VERCEL) deploy --prod
	@echo "✓ Deployed to jadecli.com"

deploy-preview: ## Deploy preview to Vercel
	$(VERCEL) deploy
	@echo "✓ Preview deployed"

# ── Sync ──────────────────────────────────────────────────────────────
sync-github: ## Sync tasks to GitHub Issues + Project
	$(PY) scripts/sync_github.py

# ── Clean ─────────────────────────────────────────────────────────────
clean: ## Remove build artifacts
	rm -rf .next/ out/ dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned"
