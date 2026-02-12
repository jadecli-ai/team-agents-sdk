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
        codegen architecture clean \
        wsl-sandbox wsl-build wsl-python-dev wsl-devtools wsl-network \
        wsl-db-clients wsl-gpu wsl-monitor wsl-quality wsl-mcp-inspector \
        wsl-install wsl-update wsl-status \
        format codegen-check architecture architecture-check \
        db-status db-branch db-migrate db-migrate-gen db-migrate-sql \
        db-diff db-seed db-branch-delete db-reset \
        deploy deploy-preview sync-github \
        golden-setup golden-sysctl golden-docker golden-mlflow golden-systemd \
        golden-health golden-benchmark golden-cleanup golden-export \
        repos-clone repos-clone-shallow repos-fetch repos-status ci-status

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

architecture: ## Generate interactive ARCHITECTURE.html from codebase
	$(PY) scripts/gen_architecture.py
	@echo "✓ ARCHITECTURE.html generated"

architecture-check: ## Check if ARCHITECTURE.html is stale
	$(PY) scripts/gen_architecture.py --check

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

# ── WSL2 Package Management ─────────────────────────────────────
#
# Tiered package installation for Ubuntu WSL2 dev environment.
# Matches Anthropic's devcontainer + Claude Code sandbox requirements.
#
# Quick start:  make wsl-install     (all tiers)
# Update all:   make wsl-update
# Check status: make wsl-status
#
# IMPORTANT: Never install nvidia-cuda-toolkit from Ubuntu repos.
# CUDA comes from Windows host driver (12.6). Only install cuda-toolkit-12-6
# from NVIDIA's wsl-ubuntu repo if you need nvcc.

# Tier 1: Claude Code sandbox (required for /sandbox)
WSL_SANDBOX := bubblewrap socat ripgrep

# Tier 2: Build toolchain (compile native extensions)
WSL_BUILD := build-essential cmake pkg-config curl wget ca-certificates \
             libssl-dev libffi-dev zlib1g-dev git gnupg2 unzip

# Tier 3: Python build deps (pyenv/asdf source builds)
WSL_PYTHON_DEV := libreadline-dev libsqlite3-dev libbz2-dev \
                  libncursesw5-dev xz-utils tk-dev libxml2-dev \
                  libxmlsec1-dev liblzma-dev

# Tier 4: Dev tools + CLI productivity
WSL_DEVTOOLS := gh jq tree fzf bat fd-find zsh vim nano less man-db \
                procps htop btop iotop sysstat dstat

# Tier 5: Network diagnostics + firewall (matches Anthropic devcontainer)
WSL_NETWORK := iproute2 dnsutils mtr iptables ipset

# Tier 6: Database clients (Neon Postgres + Redis)
WSL_DB_CLIENTS := postgresql-client redis-tools

# Tier 7: GPU monitoring (nvidia-smi comes from Windows driver stub)
WSL_GPU := nvtop lm-sensors

# All system packages combined
WSL_ALL_APT := $(WSL_SANDBOX) $(WSL_BUILD) $(WSL_PYTHON_DEV) \
               $(WSL_DEVTOOLS) $(WSL_NETWORK) $(WSL_DB_CLIENTS) $(WSL_GPU)

# Python-based tools (pip/uv)
WSL_PIP_TOOLS := nvitop gpustat glances s-tui mypy pyright bandit

# npm global tools
WSL_NPM_GLOBAL := @anthropic-ai/sandbox-runtime @modelcontextprotocol/inspector

wsl-sandbox: ## Tier 1: Claude Code sandbox (bubblewrap, socat, ripgrep)
	sudo apt-get install -y $(WSL_SANDBOX)
	sudo npm install -g @anthropic-ai/sandbox-runtime
	@echo "✓ Sandbox deps installed. Run /sandbox to verify."

wsl-build: ## Tier 2: Build toolchain (gcc, cmake, libssl-dev)
	sudo apt-get install -y $(WSL_BUILD)
	@echo "✓ Build toolchain installed"

wsl-python-dev: ## Tier 3: Python build deps (for pyenv/source builds)
	sudo apt-get install -y $(WSL_PYTHON_DEV)
	@echo "✓ Python build deps installed"

wsl-devtools: ## Tier 4: CLI productivity (gh, jq, fzf, btop)
	sudo apt-get install -y $(WSL_DEVTOOLS)
	@echo "✓ Dev tools installed"

wsl-network: ## Tier 5: Network + firewall (mtr, iptables, dnsutils)
	sudo apt-get install -y $(WSL_NETWORK)
	@echo "✓ Network tools installed"

wsl-db-clients: ## Tier 6: Database clients (psql, redis-cli)
	sudo apt-get install -y $(WSL_DB_CLIENTS)
	@echo "✓ DB clients installed"

wsl-gpu: ## Tier 7: GPU monitoring (nvtop, nvitop, gpustat)
	sudo apt-get install -y $(WSL_GPU)
	pip install nvitop gpustat
	@echo "✓ GPU monitoring installed"
	@echo "  Commands: nvidia-smi, nvtop, nvitop, gpustat"

wsl-monitor: ## System monitoring (btop, glances, s-tui, sensors)
	sudo apt-get install -y btop htop lm-sensors sysstat iotop
	pip install glances s-tui
	@echo "✓ Monitoring tools installed"
	@echo "  Commands: btop, glances, s-tui, sensors"

wsl-quality: ## Code quality tools (mypy, pyright, bandit)
	pip install mypy pyright bandit
	@echo "✓ Code quality tools installed"

wsl-mcp-inspector: ## MCP Inspector (debug/test MCP servers)
	sudo npm install -g @modelcontextprotocol/inspector
	@echo "✓ MCP Inspector installed"
	@echo "  Run: npx @modelcontextprotocol/inspector <server-command>"
	@echo "  Web UI: http://localhost:6274"

wsl-install: ## Install ALL WSL2 packages (all tiers)
	@echo "=== WSL2 Full Package Install ==="
	@echo ""
	@echo "→ Updating apt index..."
	sudo apt-get update
	@echo ""
	@echo "→ Installing system packages (Tiers 1-7)..."
	sudo apt-get install -y $(WSL_ALL_APT)
	@echo ""
	@echo "→ Installing npm global tools..."
	sudo npm install -g $(WSL_NPM_GLOBAL)
	@echo ""
	@echo "→ Installing Python tools..."
	pip install $(WSL_PIP_TOOLS)
	@echo ""
	@echo "✓ All WSL2 packages installed."
	@echo "  Run 'make wsl-status' to verify."

wsl-update: ## Update all WSL2 system + tool packages
	sudo apt-get update && sudo apt-get upgrade -y
	sudo npm update -g $(WSL_NPM_GLOBAL)
	pip install --upgrade $(WSL_PIP_TOOLS)
	@echo "✓ All WSL2 packages updated"

wsl-status: ## Show WSL2 package versions + health check
	@echo "=== WSL2 Environment Status ==="
	@echo ""
	@echo "── Sandbox ──"
	@dpkg -s bubblewrap 2>/dev/null | grep -E '^(Package|Version)' || echo "  bubblewrap: NOT INSTALLED"
	@dpkg -s socat 2>/dev/null | grep -E '^(Package|Version)' || echo "  socat: NOT INSTALLED"
	@dpkg -s ripgrep 2>/dev/null | grep -E '^(Package|Version)' || echo "  ripgrep: NOT INSTALLED"
	@npm list -g @anthropic-ai/sandbox-runtime 2>/dev/null | tail -1 || echo "  sandbox-runtime: NOT INSTALLED"
	@echo ""
	@echo "── GPU ──"
	@nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>/dev/null || echo "  nvidia-smi: NOT AVAILABLE"
	@nvcc --version 2>/dev/null | grep "release" || echo "  nvcc: NOT INSTALLED (optional)"
	@echo ""
	@echo "── Runtimes ──"
	@echo "  node: $$(node --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "  python: $$(python3 --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "  uv: $$(uv --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "  rustc: $$(rustc --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo ""
	@echo "── Tools ──"
	@echo "  gh: $$(gh --version 2>/dev/null | head -1 || echo 'NOT INSTALLED')"
	@echo "  jq: $$(jq --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "  ruff: $$(ruff --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "  mypy: $$(mypy --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "  psql: $$(psql --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo "  redis-cli: $$(redis-cli --version 2>/dev/null || echo 'NOT INSTALLED')"
	@echo ""
	@echo "── MCP Inspector ──"
	@npm list -g @modelcontextprotocol/inspector 2>/dev/null | tail -1 || echo "  NOT INSTALLED (make wsl-mcp-inspector)"

# ── Golden WSL2 Image ────────────────────────────────────────────
#
# Build/manage golden Ubuntu 26.04 WSL2 image for cloning.
# All source files live in scripts/golden/.
#
# Quick start:   make golden-setup    (install everything)
# Health check:  make golden-health   (55+ checks)
# Pre-export:    make golden-cleanup  (remove caches/secrets)

GOLDEN_DIR := $(PROJECT_DIR)/scripts/golden

golden-setup: ## Run golden image installer (all phases, requires sudo)
	sudo bash $(GOLDEN_DIR)/install.sh

golden-sysctl: ## Apply sysctl tunings only
	sudo cp $(GOLDEN_DIR)/configs/99-golden.conf /etc/sysctl.d/
	sudo sysctl --system
	@echo "✓ sysctl tunings applied (vm.swappiness=$$(sysctl -n vm.swappiness))"

golden-docker: ## Install enhanced Docker daemon config
	sudo cp $(GOLDEN_DIR)/configs/daemon.json /etc/docker/daemon.json
	sudo systemctl restart docker
	@echo "✓ Docker config updated (default-runtime=$$(docker info --format '{{.DefaultRuntime}}' 2>/dev/null))"

golden-mlflow: ## Install MLflow configs to /etc/mlflow
	sudo mkdir -p /etc/mlflow
	sudo cp $(GOLDEN_DIR)/configs/clone.env /etc/mlflow/
	sudo cp $(GOLDEN_DIR)/configs/neon.env.example /etc/mlflow/
	@echo "✓ MLflow config installed"

golden-systemd: ## Install and enable mlflow-sync timer
	sudo cp $(GOLDEN_DIR)/systemd/mlflow-sync.service /etc/systemd/system/
	sudo cp $(GOLDEN_DIR)/systemd/mlflow-sync.timer /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable --now mlflow-sync.timer
	@echo "✓ mlflow-sync timer enabled"

golden-health: ## Run distro health check (55+ checks)
	@if command -v distro-health-check &>/dev/null; then \
		distro-health-check; \
	else \
		bash $(GOLDEN_DIR)/bin/distro-health-check; \
	fi

golden-benchmark: ## Run performance baseline benchmark
	@if command -v distro-benchmark &>/dev/null; then \
		distro-benchmark; \
	else \
		bash $(GOLDEN_DIR)/bin/distro-benchmark; \
	fi

golden-cleanup: ## Pre-export cleanup (caches, logs, secrets)
	sudo bash $(GOLDEN_DIR)/cleanup.sh

golden-export: golden-cleanup ## Cleanup + show export instructions
	@echo ""
	@echo "Ready to export. On Windows PowerShell:"
	@echo "  wsl --shutdown"
	@echo "  wsl --export Ubuntu-26.04-jadecli golden-$$(date +%Y%m%d).tar"
	@echo ""
	@echo "To import as clone:"
	@echo "  wsl --import team-alpha C:\\wsl\\team-alpha golden-YYYYMMDD.tar"
	@echo "  wsl -d team-alpha -u org-jadecli -- clone-init team-alpha"

# ── Repo Management ─────────────────────────────────────────────

repos-clone: ## Clone/update all org repos (idempotent)
	@if command -v gh-clone-orgs &>/dev/null; then \
		gh-clone-orgs; \
	else \
		bash $(GOLDEN_DIR)/bin/gh-clone-orgs; \
	fi

repos-clone-shallow: ## Shallow clone secondary orgs only
	@bash $(GOLDEN_DIR)/bin/gh-clone-orgs

repos-fetch: ## Fetch all remotes across all repos
	@echo "=== Fetching all repos ==="
	@for dir in $(HOME)/projects/jadecli-ai/*/  \
	            $(HOME)/projects/jadecli/*/      \
	            $(HOME)/projects/jadecli-private/*/ \
	            $(HOME)/projects/jadecli-experimental/*/; do \
		if [ -d "$$dir/.git" ]; then \
			echo "  fetch $$(basename $$(dirname $$dir))/$$(basename $$dir)"; \
			(cd "$$dir" && git fetch --all --quiet 2>/dev/null) || true; \
		fi; \
	done
	@echo "✓ All repos fetched"

repos-status: ## Show dirty/clean status per repo
	@echo "=== Repo Status ==="
	@for dir in $(HOME)/projects/jadecli-ai/*/  \
	            $(HOME)/projects/jadecli/*/      \
	            $(HOME)/projects/jadecli-private/*/ \
	            $(HOME)/projects/jadecli-experimental/*/; do \
		if [ -d "$$dir/.git" ]; then \
			status=$$(cd "$$dir" && git status --porcelain 2>/dev/null | wc -l); \
			org=$$(basename $$(dirname $$dir)); \
			repo=$$(basename $$dir); \
			if [ "$$status" -eq 0 ]; then \
				echo "  ✓ $$org/$$repo (clean)"; \
			else \
				echo "  ✗ $$org/$$repo ($$status changes)"; \
			fi; \
		fi; \
	done

# ── CI Status ────────────────────────────────────────────────────

# ── Cache Management ────────────────────────────────────────────────

cache-stats: ## Show cache hit/miss/set/ref counters from Dragonfly
	@$(PY) -c "\
import asyncio; \
from src.cache.tool_cache import get_cache_stats; \
from src.cache.dragonfly_client import get_dragonfly; \
async def run(): \
    r = get_dragonfly(); \
    tc = len([k async for k in r.scan_iter(match='tc:*')]); \
    ctx = len([k async for k in r.scan_iter(match='ctx:*')]); \
    print('=== Cache Stats ==='); \
    print(f'  Tool cache keys (tc:*): {tc}'); \
    print(f'  Context refs (ctx:*):   {ctx}'); \
    stats = get_cache_stats(); \
    for k, v in stats.items(): print(f'  {k}: {v}'); \
asyncio.run(run())" 2>/dev/null || echo "  Dragonfly not available (check PRJ_DRAGONFLY_URL)"

cache-flush: ## Delete all tc:* and ctx:* cache keys
	@$(PY) -c "\
import asyncio; \
from src.cache.tool_cache import flush_cache; \
async def run(): \
    n = await flush_cache(); \
    print(f'Flushed {n} cache keys'); \
asyncio.run(run())" 2>/dev/null || echo "  Dragonfly not available"

# ── CI Status ────────────────────────────────────────────────────

ci-status: ## Show status of free-tier CI integrations
	@echo "=== CI Integration Status ==="
	@echo ""
	@echo "── GitHub Actions ──"
	@gh run list --limit 5 2>/dev/null || echo "  Not available (run: gh auth login)"
	@echo ""
	@echo "── Release Please ──"
	@gh pr list --label "autorelease: pending" 2>/dev/null || echo "  No pending releases"
	@echo ""
	@echo "── Vercel ──"
	@npx vercel ls --limit 3 2>/dev/null || echo "  Not configured"
