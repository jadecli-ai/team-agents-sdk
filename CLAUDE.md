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

## Automated Changelog (release-please)

Uses [release-please](https://github.com/googleapis/release-please) (same as Anthropic SDKs):

- `.release-please-manifest.json` — tracks current version
- `release-please-config.json` — changelog sections, version bump rules
- `.github/workflows/release.yml` — creates release PR on every push to main

On conventional commit push to main:
1. release-please opens/updates a "Release PR" with bumped version + CHANGELOG.md
2. Merging the Release PR creates a GitHub Release + git tag `v{version}`
3. Version auto-bumps in `pyproject.toml` and `package.json`

To preview: `git log --oneline $(git describe --tags --abbrev=0 2>/dev/null)..HEAD`

## Architecture Visualization

Interactive HTML diagram auto-generated from codebase:

```bash
make architecture       # Generate ARCHITECTURE.html (42 files, 54 edges)
make architecture-check # Verify it's not stale
```

- Shows backend, frontend, middleware, schema, test, infra, CI layers
- Click any node to see its dependencies and dependents
- Filter by layer using toolbar buttons
- External services (Neon, Vercel, GitHub, Claude SDK, MLflow) shown on right
- **Auto-updated on every PR and release** via `.github/workflows/architecture.yml`
- PR CI commits the updated HTML automatically — architecture is always current

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
| `make architecture` | Generate interactive ARCHITECTURE.html |
| `make architecture-check` | Verify ARCHITECTURE.html is current |
| `make apps-setup` | Run all GitHub App install scripts |
| `make claude-sync` | Sync Claude OAuth tokens to secrets |
| `make sync-github` | Sync tasks → GitHub Issues + Project |
| `make clean` | Remove build artifacts |

## Permission Settings

Two settings files control Claude Code permissions:

- **`.claude/settings.json`** — project-level, inherits from `.claude-org/settings.json` (committed)
- **`.claude/settings.local.json`** — local dev overrides (gitignored)

The local file auto-allows all tools (`Bash(*)`, `Read(*)`, `Edit(*)`, `Write(*)`, `WebFetch(*)`, `Task(*)`, `mcp__*`) while keeping hard deny rules for:

| Category | Blocked |
|----------|---------|
| Destructive git | `push --force`, `reset --hard`, `clean -fdx` |
| Filesystem nuke | `rm -rf /`, `~/`, `.` |
| Privilege escalation | `sudo *` |
| Public publishing | npm/yarn/twine/cargo publish, docker push |
| Infra destruction | `kubectl delete namespace`, `terraform destroy` |
| Secrets | `.ssh/`, `.gnupg/`, AWS creds, `.env*`, `*.pem`, `*.key` |

To reset to prompted mode: delete `.claude/settings.local.json`.

## Slash Commands (L0-L9)

Monotonic command system where each level depends only on levels below it:

| Level | Command | Purpose |
|-------|---------|---------|
| L0 | `/check` | Fail-fast: lint + test + codegen-check + architecture-check |
| L1 | `/schema <name>` | Create/modify semantic YAML table definition |
| L2 | `/model <name>` | Generate Pydantic model from YAML (inherits BaseEntity) |
| L3 | `/table <name>` | Generate SQLAlchemy Table + Drizzle schema |
| L4 | `/crud <name>` | Wire up Crud(table) instance |
| L5 | `/hook <purpose>` | Create Agent SDK hook |
| L6 | `/test <target>` | Generate test file (TDD red/green/refactor) |
| L7 | `/migrate <desc>` | Generate + apply Neon migration (branch workflow) |
| L8 | `/sync <scope>` | Sync tasks → GitHub Issues + Projects |
| L9 | `/ship <name> - <desc>` | Full pipeline: L0→L1→L2→L3→L4→L6→L7→commit |

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
