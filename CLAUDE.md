# CLAUDE.md — jadecli-team-agents-sdk

## What This Is

Multi-agent task system: Neon Postgres + Claude Agent SDK + MLflow 3.9 tracing.
Semantic YAML schemas generate both Pydantic (Python) and Drizzle (TypeScript).
Dashboard deploys to jadecli.com via Vercel + Next.js.

## Quick Start

```bash
make install        # uv pip install + npm install
make test           # pytest — must pass before any commit
make dev            # Next.js dev server (Turbopack)
make db-status      # Verify Neon connection + env vars
make apps-setup     # Generate all GitHub App config files
```

## Fail-Fast Checks

Run these before starting work. All must pass:

```bash
make test           # 42 tests (models, crud, hooks, db)
make lint           # ruff check + format
make codegen-check  # Semantic YAML → schema consistency
```

If `PRJ_NEON_DATABASE_URL` is set, `test_db.py` runs live round-trips. Otherwise skips.

## Architecture At a Glance

```
semantic/*.yaml          <- SINGLE SOURCE OF TRUTH for all tables
    |
    ├── src/models/*.py      Pydantic v2 (validators, model_validators)
    ├── src/db/tables.py     SQLAlchemy Table objects (indexes, FKs, checks)
    ├── app/db/schema.ts     Drizzle pgTable definitions
    └── migrations/*.sql     DDL for Neon

src/hooks/               <- Claude Agent SDK hooks → write to Neon
src/db/crud.py           <- Generic async CRUD (create/get/find/update/delete/increment)
src/get_env.py           <- All env access — never os.environ directly
app/                     <- Next.js dashboard (Vercel)
```

## File Frontmatter Convention

Every Python and TypeScript source file MUST include a frontmatter docstring/comment at the top:

**Python** (module docstring):
```python
"""Short description of this module.

schema: tasks                    # Which semantic/*.yaml this implements
depends_on:
  - src/models/enums.py          # Files this module imports from
  - src/models/base.py
depended_by:
  - src/db/tables.py             # Files that import from this module
  - tests/test_models.py
semver: minor                    # Change impact: patch|minor|major
"""
```

**TypeScript** (block comment):
```typescript
/**
 * Short description of this module.
 *
 * @schema tasks
 * @depends_on lib/db.ts
 * @depended_by app/page.tsx
 * @semver minor
 */
```

**Rules**:
- [ ] Add `depends_on` when you import from another project file
- [ ] Add `depended_by` when another project file imports from you
- [ ] Update BOTH sides when adding a new dependency link
- [ ] Set `semver: major` if you change a public export signature
- [ ] Set `semver: minor` if you add new exports
- [ ] Set `semver: patch` for internal-only changes

## Semantic Schema Rules

Schemas in `semantic/*.yaml` are the single source of truth. When changing a table:

- [ ] Edit the YAML first
- [ ] Run `make codegen` to regenerate Drizzle schema
- [ ] Manually update the matching Pydantic model to match
- [ ] Manually update `src/db/tables.py` to match
- [ ] Run `make codegen-check` to verify consistency
- [ ] Write a migration: `make db-migrate-gen MSG="describe change"`

**Never** edit generated files (`app/db/schema.ts`) by hand — they get overwritten.

## Environment Variables

All access goes through `src/get_env.py`:

```python
from src.get_env import env
url = env("PRJ_NEON_DATABASE_URL")           # raises KeyError if missing
uri = env("PRJ_MLFLOW_TRACKING_URI", default="http://localhost:5000")
```

- [ ] Never use `os.environ` or `os.getenv` directly
- [ ] Never log, print, or include env values in error messages
- [ ] Add new keys to `env.template` with the `ORG_` or `PRJ_` prefix convention
- [ ] Run `env.check()` to audit which keys are set vs missing

## Test-Driven Development

**Red/Green/Refactor cycle — always**:

1. **Red**: Write a failing test that defines the expected behavior
2. **Green**: Write the minimum code to make it pass
3. **Refactor**: Clean up while keeping tests green

**Test priority order** (most valuable first):

1. **Live integration tests** — real Neon DB, real SDK calls, real data
2. **Live data tests** — seed + query + assert against actual Postgres
3. **Unit tests with real objects** — instantiate Pydantic models, validate constraints
4. **Mock tests** — LAST RESORT only when external service is unavailable

**Rules**:
- [ ] Tests that hit Neon: guard with `@pytest.mark.skipif(not env("PRJ_NEON_DATABASE_URL", default=None))`
- [ ] Tests that mock: add a comment explaining WHY the mock is necessary
- [ ] Every bug fix starts with a failing test that reproduces the bug
- [ ] `make test` must pass before every commit — CI enforces this
- [ ] Never `continue-on-error` or `try/except pass` in tests

## Patterns to Follow

- [ ] **Fail fast, fail loud**: raise on bad state, never silently degrade
- [ ] **`env()` for all config**: single accessor, never leaks values
- [ ] **`Crud(table)` for DB ops**: don't write raw SQLAlchemy in business logic
- [ ] **Pydantic `model_validator`**: cross-field constraints live on the model
- [ ] **`(str, Enum)` pattern**: all enums inherit `(str, Enum)`, not `StrEnum`
- [ ] **`datetime.now(timezone.utc)`**: never `datetime.utcnow()` (deprecated)
- [ ] **Async everywhere**: `asyncpg` + `AsyncSession`, never sync DB calls
- [ ] **Hooks are fire-and-forget**: activity_tracker catches its own exceptions so agent runs never crash from logging failures
- [ ] **Semantic YAML first**: change the schema, then update code to match
- [ ] **Use Anthropic SDK patterns**: follow `claude-agent-sdk` and `anthropic-sdk-python` conventions for client setup, error handling, streaming

## Anti-Patterns to Avoid

- [ ] **`os.environ` / `os.getenv`** — use `env()` from `src/get_env.py`
- [ ] **`datetime.utcnow()`** — deprecated; use `datetime.now(timezone.utc)`
- [ ] **Silent failures** — no bare `except: pass`, no `continue-on-error` in CI
- [ ] **Mock-heavy tests** — if you can test against real Neon, do it
- [ ] **Hand-editing generated files** — `app/db/schema.ts` is generated; edit YAML instead
- [ ] **Sync DB calls** — no `psycopg2`, no sync `create_engine`
- [ ] **Secrets in code/logs** — `env()` never exposes values; keep it that way
- [ ] **`StrEnum`** — requires Python 3.11; `(str, Enum)` works on 3.10+
- [ ] **Gradual degradation** — don't catch and continue; raise and fix the root cause
- [ ] **Installing `nvidia-cuda-toolkit` from Ubuntu repos** — conflicts with CUDA 12.6 (WSL2 host)

## Conventional Commits + Semver

Every commit message follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

| Type | Semver bump | When |
|------|-------------|------|
| `fix` | PATCH | Bug fix, no API change |
| `feat` | MINOR | New feature, backward compatible |
| `feat!` or `BREAKING CHANGE:` | MAJOR | Breaking public API change |
| `chore` | none | CI, deps, configs (no user-facing change) |
| `docs` | none | Documentation only |
| `test` | none | Adding/fixing tests |
| `refactor` | none | Code change that doesn't fix a bug or add a feature |

**Scopes**: `models`, `db`, `hooks`, `sync`, `dashboard`, `ci`, `schema`, `deps`

**Examples**:
```
feat(models): add deadline_at field to Task
fix(hooks): prevent duplicate PreToolUse events for same tool
feat!(db): rename actual_cost_usd to total_cost_usd
chore(deps): bump claude-agent-sdk to 0.2.0
test(crud): add live Neon round-trip for increment
```

## Automated Changelog

Changelog is generated from conventional commits. The CI pipeline:

1. Parses commit messages since last tag
2. Groups by type (Features, Fixes, Breaking Changes)
3. Bumps version in `pyproject.toml` based on highest semver type
4. Generates `CHANGELOG.md` entry
5. Creates git tag `v{version}`

To preview: `git log --oneline $(git describe --tags --abbrev=0)..HEAD`

## Neon Branching Workflow

Safe migration path — never run DDL directly on main:

```bash
make db-branch          # Create Neon branch (named after git branch)
make db-migrate         # Run Alembic on branch
make test               # Verify against branch
make db-diff            # Compare branch schema vs main
make db-promote         # Run same migration on main
make db-branch-delete   # Clean up
```

PR-based workflow is automated via `.github/workflows/neon-branch.yml`.

## MLflow Tracing

```python
import mlflow
mlflow.anthropic.autolog()  # One line — captures all SDK calls
```

- Traces auto-capture: tool calls, agent turns, costs, durations
- Dashboard: `mlflow server --port 5000` then http://localhost:5000
- Experiment name: `env("PRJ_MLFLOW_EXPERIMENT_NAME")`

### Trace-Discovered Mistakes

When an MLflow trace reveals a bug or anti-pattern, add it here so it's never repeated:

| Date | Trace | Mistake | Fix |
|------|-------|---------|-----|
| _template_ | _trace_id_ | _what went wrong_ | _what to do instead_ |

## Key Commands Reference

| Command | What it does |
|---------|-------------|
| `make install` | Install Python (uv) + Node deps |
| `make test` | Run all pytest tests |
| `make lint` | Ruff check + format verification |
| `make format` | Auto-fix lint + formatting |
| `make build` | Build Next.js for production |
| `make dev` | Start Next.js dev server |
| `make deploy` | Production deploy to Vercel |
| `make deploy-preview` | Preview deploy to Vercel |
| `make db-status` | Show Neon branches + env check |
| `make db-branch` | Create Neon branch for safe migration |
| `make db-migrate` | Run Alembic upgrade head |
| `make db-migrate-sql` | Apply raw SQL migration |
| `make db-diff` | Schema diff: main vs branch |
| `make db-seed` | Seed sample data |
| `make codegen` | YAML → Drizzle schema |
| `make codegen-check` | Validate YAML consistency |
| `make apps-setup` | Run all GitHub App install scripts |
| `make claude-sync` | Sync Claude OAuth tokens to secrets |
| `make sync-github` | Sync tasks → GitHub Issues + Project |
| `make clean` | Remove build artifacts |

## Directory Map

```
semantic/                 Cube.js-inspired YAML schemas (source of truth)
src/get_env.py            Safe env accessor (never os.environ)
src/models/               Pydantic v2 models + enums
src/db/engine.py          Async SQLAlchemy engine (Neon)
src/db/tables.py          SQLAlchemy Table objects
src/db/crud.py            Generic async CRUD
src/db/alembic/           Async Alembic migrations
src/hooks/                Claude Agent SDK hooks (activity + cost → Neon)
src/sync/                 GitHub Issues + Project sync
app/                      Next.js dashboard (Vercel)
app/db/schema.ts          Drizzle pgTable (generated — don't hand-edit)
lib/db.ts                 Neon serverless client
scripts/codegen.py        YAML → TypeScript generator
scripts/installations/    Per-app setup scripts (7 GitHub Apps)
tests/                    Pytest (models, crud, hooks, db integration)
migrations/               Raw SQL DDL
docs/references/          Saved web-fetched reference docs
research/                 Initial architecture research
env.template              Key registry (no values — committed)
.env                      Local values (gitignored — never committed)
```
