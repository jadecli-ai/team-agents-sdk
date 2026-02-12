# /migrate $ARGUMENTS

Generate and apply a Neon migration using the safe branching workflow.

## Context
- Read `src/db/tables.py` for current table definitions
- Read `migrations/` for existing SQL migrations
- Read the Neon branching workflow in CLAUDE.md

## Steps
1. Run `make db-branch` to create a Neon branch (safe sandbox)
2. Generate migration: `make db-migrate-gen MSG="$ARGUMENTS"`
3. Review the generated migration file in `src/db/alembic/versions/`
4. Apply: `make db-migrate`
5. Run `make test` against the branch
6. Report the migration file path and diff summary

Do NOT run `make db-promote` — that's a manual decision for the user.

## Output
1. Generated Alembic migration file
2. Test results against the branch
