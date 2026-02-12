"""Hook composition: merge multiple hook sets with chained handlers.

Single handler per event: passthrough (zero overhead).
Multiple handlers same event: chained sequentially, independent try/except.

depends_on: []
depended_by:
  - src/cache/__init__.py
  - src/hooks/__init__.py
  - tests/test_cache.py
semver: minor
"""

from __future__ import annotations

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


def compose_hooks(*hook_dicts: dict[str, Callable]) -> dict[str, Callable]:
    """Merge multiple hook dicts into one. Same-event handlers chain sequentially.

    Args:
        *hook_dicts: Dicts mapping event names (e.g. "PreToolUse") to async callables.

    Returns:
        A single dict where each event maps to a handler that calls all
        registered handlers in order, with independent error isolation.
    """
    merged: dict[str, list[Callable]] = {}

    for hooks in hook_dicts:
        for event, handler in hooks.items():
            merged.setdefault(event, []).append(handler)

    result: dict[str, Callable] = {}
    for event, handlers in merged.items():
        if len(handlers) == 1:
            # Single handler — zero-overhead passthrough
            result[event] = handlers[0]
        else:
            # Multiple handlers — chained with isolation
            result[event] = _make_chain(event, handlers)

    return result


def _make_chain(event: str, handlers: list[Callable]) -> Callable:
    """Create a chained handler that calls all handlers with error isolation."""

    async def chained(*args: Any, **kwargs: Any) -> None:
        for handler in handlers:
            try:
                await handler(*args, **kwargs)
            except Exception:
                logger.exception(
                    "Hook handler failed for event %s: %s",
                    event,
                    handler.__qualname__,
                )

    chained.__qualname__ = f"chained_{event}"
    return chained
