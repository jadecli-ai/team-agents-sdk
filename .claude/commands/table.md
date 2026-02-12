# /table $ARGUMENTS

Add SQLAlchemy Table definition and regenerate Drizzle schema.

## Context
- Read `semantic/$ARGUMENTS.yaml` for column definitions
- Read `src/db/tables.py` for existing table patterns (metadata, column types, indexes, FKs)
- Read `scripts/codegen.py` to understand Drizzle generation

## Rules
- Add Table object to `src/db/tables.py` using same metadata object
- Map YAML types: uuid→sa.UUID, varchar→sa.String(N), float→sa.Float, timestamptz→sa.DateTime(timezone=True), integer→sa.Integer
- Add Index objects for columns listed in YAML `indexes`
- Add ForeignKey for any column referencing another table
- Add CheckConstraint for any YAML `check_constraints`
- Update frontmatter in `src/db/tables.py` (add schema reference)
- Run `make codegen` to regenerate `app/db/schema.ts`
- Run `make codegen-check` to validate

## Output
1. Edit `src/db/tables.py` — add new Table object
2. Run `make codegen` (regenerates Drizzle)
