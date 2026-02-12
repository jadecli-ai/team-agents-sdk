# /ship $ARGUMENTS

Full pipeline: add a new entity from semantic YAML through to migration and commit.

Parse $ARGUMENTS as: "{entity_name} - {description}"

## Pipeline (sequential — each step depends on the previous)

1. **L0 /check**: Run fail-fast checks. STOP if any fail.
2. **L1 /schema**: Create `semantic/{entity_name}.yaml` with the described columns
3. **L2 /model**: Generate Pydantic model inheriting BaseEntity
4. **L3 /table**: Add SQLAlchemy Table + regenerate Drizzle schema
5. **L4 /crud**: Wire up Crud(table) instance
6. **L6 /test**: Generate tests (run RED first to confirm tests catch missing behavior)
7. **Run tests**: `make test` — expect GREEN after model+table+crud are in place
8. **L7 /migrate**: Generate Neon migration (do NOT auto-promote)
9. **Commit**: `git add` all new/modified files, conventional commit: `feat({entity_name}): add {entity_name} entity with model, table, crud, tests`
10. **L0 /check**: Final validation pass

## Rules
- STOP on any failure — never continue past a broken step
- Each file MUST have frontmatter (depends_on, depended_by, semver)
- Update BOTH sides of any new dependency link
- Run `make architecture` at the end to update ARCHITECTURE.html

## Output
Summary table: step | status | files created/modified
