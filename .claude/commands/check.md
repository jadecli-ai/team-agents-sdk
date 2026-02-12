# /check

Run all fail-fast validation checks. Report pass/fail for each.

## Steps
1. Run `make lint` — ruff check + format verification
2. Run `make test` — all pytest tests (42 tests)
3. Run `make codegen-check` — YAML schema consistency
4. Run `make architecture-check` — ARCHITECTURE.html staleness

Report each check as PASS or FAIL. Stop on first failure and show the error output.

Do NOT proceed to fix anything — just report status.
