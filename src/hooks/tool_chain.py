"""Automated tool chaining hooks.

Defines common tool call sequences that execute as atomic chains
rather than individual agent decisions. Reduces latency by eliminating
round-trips for predictable sequences.

depends_on:
  - src/hooks/activity_tracker.py
depended_by:
  - src/hooks/__init__.py
  - src/cache/compose.py
  - tests/test_hooks.py
semver: minor
"""

from __future__ import annotations

import logging
from typing import Awaitable, Callable

logger = logging.getLogger(__name__)

# Chain registry: name -> async callable
_chains: dict[str, Callable[..., Awaitable[str]]] = {}


def register_chain(name: str, fn: Callable[..., Awaitable[str]]) -> None:
    """Register a named tool chain."""
    _chains[name] = fn
    logger.debug("Registered tool chain: %s", name)


def get_chain(name: str) -> Callable[..., Awaitable[str]] | None:
    """Look up a registered chain by name."""
    return _chains.get(name)


def list_chains() -> list[str]:
    """List all registered chain names."""
    return list(_chains.keys())


def clear_chains() -> None:
    """Remove all registered chains."""
    _chains.clear()


def get_chain_hooks() -> dict:
    """Returns hooks for tool chaining.

    PostToolUse: Detects chain triggers (e.g., Glob result
    could auto-trigger Read for each file).
    """
    return {
        "PostToolUse": _chain_detector,
    }


async def _chain_detector(
    tool_name: str, tool_input: dict, tool_response: str | None = None, **_kwargs
) -> None:
    """Detect opportunities for chain execution.

    Currently logs chain opportunities. Future: auto-execute
    when confidence is high and chain is registered.
    """
    if tool_name == "Glob" and tool_response:
        lines = [line for line in tool_response.strip().splitlines() if line.strip()]
        if 1 <= len(lines) <= 5:
            logger.debug(
                "Chain opportunity: Glob returned %d files — consider batch Read",
                len(lines),
            )
