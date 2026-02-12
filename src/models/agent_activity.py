"""AgentActivity model matching semantic/agent_activity.yaml."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from pydantic import Field

from src.models.base import BaseEntity
from src.models.enums import AgentRole


class AgentActivity(BaseEntity):
    """Hook event log capturing agent tool use, cost, and timing."""

    task_id: UUID | None = None
    subtask_id: UUID | None = None
    agent_name: str = Field(..., max_length=50)
    agent_role: AgentRole | None = None
    session_id: str | None = Field(default=None, max_length=100)
    hook_event: str = Field(..., max_length=20)
    tool_name: str | None = Field(default=None, max_length=50)
    tool_input_summary: str | None = Field(default=None, max_length=2000)
    tool_response_summary: str | None = Field(default=None, max_length=2000)
    duration_ms: int | None = Field(default=None, ge=0)
    cost_usd: float | None = Field(default=None, ge=0)
    num_turns: int | None = Field(default=None, ge=0)
    event_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
