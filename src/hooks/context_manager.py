"""Dynamic context pruning hooks.

SDK constraint: PreToolUse hooks return None (cannot short-circuit).
Context management happens via PostToolUse observation and
pre-turn summarization.

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
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ContextState:
    """Tracks context pressure for a single agent run."""

    total_output_bytes: int = 0
    tool_call_count: int = 0
    summarization_requested: bool = False

    # Thresholds
    OUTPUT_WARN_BYTES: int = field(default=50_000, repr=False)  # 50KB — log warning
    OUTPUT_PRUNE_BYTES: int = field(default=150_000, repr=False)  # 150KB — request summarization
    MAX_TOOL_CALLS: int = field(default=25, repr=False)  # safety limit per turn


_state = ContextState()


def get_context_hooks() -> dict:
    """Returns hooks for context management.

    PostToolUse: Tracks output size, flags for pruning.
    PreToolUse: Injects summarization directive when flagged.
    """
    return {
        "PostToolUse": _post_tool_observer,
        "PreToolUse": _pre_tool_advisor,
    }


async def _post_tool_observer(
    tool_name: str, tool_input: dict, tool_response: str | None = None, **_kwargs
) -> None:
    """Track cumulative output size. Flag when threshold exceeded."""
    result_text = tool_response or ""
    _state.total_output_bytes += len(result_text.encode("utf-8"))
    _state.tool_call_count += 1

    if _state.total_output_bytes > _state.OUTPUT_WARN_BYTES and not _state.summarization_requested:
        logger.info(
            "Context pressure warning: %d bytes across %d tool calls",
            _state.total_output_bytes,
            _state.tool_call_count,
        )

    if _state.total_output_bytes > _state.OUTPUT_PRUNE_BYTES:
        _state.summarization_requested = True
        logger.warning(
            "Context pruning requested: %d bytes exceeds %d threshold",
            _state.total_output_bytes,
            _state.OUTPUT_PRUNE_BYTES,
        )

    if _state.tool_call_count >= _state.MAX_TOOL_CALLS:
        _state.summarization_requested = True
        logger.warning(
            "Context pruning requested: %d tool calls reached limit",
            _state.tool_call_count,
        )


async def _pre_tool_advisor(tool_name: str, tool_input: dict, **_kwargs) -> None:
    """Log advisory when context pressure is high.

    SDK constraint: cannot return modified input or block.
    .claude/rules/context.md enforces that agents summarize
    before continuing when pressure_pct > 80%.
    """
    if _state.summarization_requested:
        logger.info(
            "Context pressure high (%.1f%%) — summarize before continuing",
            _state.total_output_bytes / _state.OUTPUT_PRUNE_BYTES * 100,
        )


def reset_context_state() -> None:
    """Reset between agent runs."""
    global _state
    _state = ContextState()


def get_context_stats() -> dict:
    """Return current context pressure metrics."""
    return {
        "total_output_bytes": _state.total_output_bytes,
        "tool_call_count": _state.tool_call_count,
        "summarization_requested": _state.summarization_requested,
        "pressure_pct": round(_state.total_output_bytes / _state.OUTPUT_PRUNE_BYTES * 100, 1),
    }
