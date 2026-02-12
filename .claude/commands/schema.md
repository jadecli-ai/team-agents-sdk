# /schema $ARGUMENTS

Create or modify a semantic YAML table definition in `semantic/`.

## Context
- Read `semantic/tasks.yaml` as the canonical format example
- Read `semantic/_enums.yaml` for existing enum types
- Read all other `semantic/*.yaml` files to understand existing tables and joins
- Follow the Cube.js-inspired format: columns, dimensions, measures, joins, indexes, model_validators

## Rules
- Every table MUST have: id (uuid PK), schema_version (int default 1), created_at, updated_at
- Use existing enums from `_enums.yaml` where applicable; add new enums there if needed
- Foreign keys reference other tables by `{table_name}.id`
- Include at least one dimension and one measure for dashboard analytics
- Add model_validators for any cross-field business rules
- Timestamps are always `timestamptz`, never plain `timestamp`

## Output
Write ONE file: `semantic/{name}.yaml`
If modifying: edit the existing file, don't recreate

After writing, run `make codegen-check` to validate.
