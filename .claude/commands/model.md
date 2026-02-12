# /model $ARGUMENTS

Generate a Pydantic v2 model from `semantic/$ARGUMENTS.yaml`.

## Context
- Read `semantic/$ARGUMENTS.yaml` for the table definition
- Read `semantic/_enums.yaml` for enum types
- Read `src/models/base.py` for BaseEntity (MUST inherit from it)
- Read `src/models/enums.py` for existing enum classes
- Read `src/models/task.py` as the canonical model example (most complete)

## Rules
- Inherit from `BaseEntity` — never redeclare id, schema_version, created_at, updated_at
- Use `(str, Enum)` pattern, NOT `StrEnum` (Python 3.10 compat)
- Map YAML `validators` to Pydantic `Field(ge=0)`, `Field(min_length=1)`, etc.
- Map YAML `model_validators` to `@model_validator(mode="after")` methods
- Use `ConfigDict(from_attributes=True, str_strip_whitespace=True, use_enum_values=True)`
- Add frontmatter: schema, depends_on, depended_by, semver
- All timestamps: `datetime | None = None` (except created_at/updated_at from base)
- Costs: `float = Field(default=0.0, ge=0)`
- New enums go in `src/models/enums.py`, not inline

## Output
1. If new enums needed: edit `src/models/enums.py`
2. Write `src/models/$ARGUMENTS.py`
3. Update `src/models/__init__.py` to re-export the new model
