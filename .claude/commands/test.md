# /test $ARGUMENTS

Generate a test file following TDD red/green/refactor.

## Context
- Read `tests/test_models.py` for model validation test patterns
- Read `tests/test_crud.py` for CRUD round-trip test patterns
- Read `tests/test_hooks.py` for hook callback test patterns
- Read `tests/test_db.py` for live Neon integration test patterns

## Rules — Test Priority Order (most valuable first)
1. **Live integration tests** — real Neon DB round-trips. Guard with `@pytest.mark.skipif(not env("PRJ_NEON_DATABASE_URL", default=None))`
2. **Unit tests with real objects** — instantiate Pydantic models, validate constraints
3. **Mock tests** — LAST RESORT, with comment explaining WHY mock is needed

## Test Structure
- Each test function tests ONE behavior
- Test names: `test_{table}_{behavior}` (e.g., `test_sprint_status_transition`)
- Validators: test both valid and invalid inputs (expect `ValidationError`)
- model_validators: test cross-field constraint enforcement
- CRUD: test create→read→update→delete cycle
- Hooks: test that callbacks don't raise on success AND on DB failure

## Output
1. Write `tests/test_{name}.py`
2. Run `make test` to verify (expect RED for new tests of unimplemented features)
