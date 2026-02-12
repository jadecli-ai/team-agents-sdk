"""Claude Agent SDK hooks that log agent activity to Neon Postgres.

Usage:
    from src.hooks import get_activity_hooks

    options = ClaudeAgentOptions(
        hooks=get_activity_hooks(task_id=my_task_id, agent_name="code-reviewer"),
    )
"""

from __future__ import annotations

import time
import logging
from uuid import UUID

import sqlalchemy as sa

from src.db.engine import get_session_factory
from src.db.tables import agent_activity

logger = logging.getLogger(__name__)

# In-flight tool start times keyed by (session_id, tool_name)
_tool_start_times: dict[tuple[str | None, str | None], float] = {}


def _truncate(text: str | None, max_len: int = 2000) -> str | None:
    if text is None:
        return None
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


async def _log_event(
    *,
    task_id: UUID | None,
    agent_name: str,
    agent_role: str | None,
    session_id: str | None,
    hook_event: str,
    tool_name: str | None = None,
    tool_input_summary: str | None = None,
    tool_response_summary: str | None = None,
    duration_ms: int | None = None,
    cost_usd: float | None = None,
    num_turns: int | None = None,
) -> None:
    """Insert a single agent_activity row. Silently catches DB errors."""
    try:
        session_factory = get_session_factory()
        async with session_factory() as session:
            await session.execute(
                sa.insert(agent_activity).values(
                    task_id=task_id,
                    agent_name=agent_name,
                    agent_role=agent_role,
                    session_id=session_id,
                    hook_event=hook_event,
                    tool_name=tool_name,
                    tool_input_summary=_truncate(tool_input_summary),
                    tool_response_summary=_truncate(tool_response_summary),
                    duration_ms=duration_ms,
                    cost_usd=cost_usd,
                    num_turns=num_turns,
                )
            )
            await session.commit()
    except Exception:
        logger.exception("Failed to log agent activity event")


def get_activity_hooks(
    task_id: UUID | None = None,
    agent_name: str = "unknown",
    agent_role: str | None = None,
) -> dict:
    """Return a hooks dict for ClaudeAgentOptions.

    Returns:
        Dict with PreToolUse, PostToolUse, SubagentStop, Stop callbacks.
    """

    async def on_pre_tool_use(tool_name: str, tool_input: dict, *, session_id: str | None = None, **_kwargs) -> None:
        _tool_start_times[(session_id, tool_name)] = time.monotonic()
        await _log_event(
            task_id=task_id,
            agent_name=agent_name,
            agent_role=agent_role,
            session_id=session_id,
            hook_event="PreToolUse",
            tool_name=tool_name,
            tool_input_summary=str(tool_input)[:2000],
        )

    async def on_post_tool_use(
        tool_name: str,
        tool_input: dict,
        tool_response: str | None = None,
        *,
        session_id: str | None = None,
        **_kwargs,
    ) -> None:
        start = _tool_start_times.pop((session_id, tool_name), None)
        duration_ms = int((time.monotonic() - start) * 1000) if start else None
        await _log_event(
            task_id=task_id,
            agent_name=agent_name,
            agent_role=agent_role,
            session_id=session_id,
            hook_event="PostToolUse",
            tool_name=tool_name,
            tool_input_summary=str(tool_input)[:2000],
            tool_response_summary=_truncate(tool_response),
            duration_ms=duration_ms,
        )

    async def on_subagent_stop(*, session_id: str | None = None, num_turns: int | None = None, **_kwargs) -> None:
        await _log_event(
            task_id=task_id,
            agent_name=agent_name,
            agent_role=agent_role,
            session_id=session_id,
            hook_event="SubagentStop",
            num_turns=num_turns,
        )

    async def on_stop(*, session_id: str | None = None, num_turns: int | None = None, cost_usd: float | None = None, **_kwargs) -> None:
        await _log_event(
            task_id=task_id,
            agent_name=agent_name,
            agent_role=agent_role,
            session_id=session_id,
            hook_event="Stop",
            num_turns=num_turns,
            cost_usd=cost_usd,
        )

    return {
        "PreToolUse": on_pre_tool_use,
        "PostToolUse": on_post_tool_use,
        "SubagentStop": on_subagent_stop,
        "Stop": on_stop,
    }
