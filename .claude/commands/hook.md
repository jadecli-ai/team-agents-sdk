# /hook $ARGUMENTS

Create a Claude Agent SDK hook.

## Context
- Read `src/hooks/activity_tracker.py` as THE canonical pattern
- Read `src/hooks/cost_tracker.py` for simpler hook example
- Read `src/hooks/__init__.py` for the re-export pattern

## Rules
- Factory function returns a dict of hook callbacks: {PreToolUse, PostToolUse, SubagentStop, Stop}
- Each callback is async, takes **_kwargs for forward compat
- All DB writes wrapped in try/except with logger.exception (fire-and-forget: never crash the agent)
- Use `_truncate()` for any string fields (max 2000 chars)
- Import tables and session factory from `src/db/`
- Add frontmatter with depends_on and depended_by
- Update `src/hooks/__init__.py` to re-export

## Output
1. Write `src/hooks/{name}.py`
2. Update `src/hooks/__init__.py`
