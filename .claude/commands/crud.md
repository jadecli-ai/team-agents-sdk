# /crud $ARGUMENTS

Wire up Crud(table) for the new table.

## Context
- Read `src/db/crud.py` for the generic Crud class (create, get, find, update, delete, increment, count, exists)
- Read `src/db/tables.py` to import the new table object
- Read `src/hooks/cost_tracker.py` as example of table-specific Crud usage

## Rules
- Import the table from `src/db/tables.py`
- Instantiate `Crud(table_name)` at module level
- Only add custom async functions if the table needs operations beyond generic CRUD (e.g., atomic multi-table updates, complex queries)
- If the table is simple: just document the Crud instance in a docstring, no custom module needed
- Update `src/db/__init__.py` to re-export the new Crud instance

## Output
1. If custom ops needed: write `src/db/{table_name}_ops.py`
2. Otherwise: add Crud instance to existing code or `src/db/__init__.py`
