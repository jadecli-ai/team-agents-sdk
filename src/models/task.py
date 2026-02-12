"""Task and TaskDependency models matching semantic/tasks.yaml."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field, model_validator

from src.models.base import BaseEntity
from src.models.enums import AgentRole, TaskPriority, TaskStatus


class Task(BaseEntity):
    """A tracked task for multi-agent team runs."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus = TaskStatus.pending
    priority: TaskPriority = TaskPriority.medium
    assigned_agent: AgentRole | None = None
    session_id: str | None = Field(default=None, max_length=100)
    estimated_cost_usd: float = Field(default=0.0, ge=0)
    actual_cost_usd: float = Field(default=0.0, ge=0)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    due_at: datetime | None = None
    github_issue_number: int | None = Field(default=None, ge=1)
    github_project_item_id: str | None = Field(default=None, max_length=50)
    blocker_ids: list[UUID] = Field(default_factory=list)
    subtask_ids: list[UUID] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_status_constraints(self) -> Task:
        if self.status == TaskStatus.completed and self.completed_at is None:
            raise ValueError("Completed tasks must have completed_at set")
        if self.status == TaskStatus.in_progress and self.started_at is None:
            raise ValueError("In-progress tasks must have started_at set")
        if self.status == TaskStatus.blocked and not self.blocker_ids:
            raise ValueError("Blocked tasks must have at least one blocker_id")
        return self


class TaskDependency(BaseEntity):
    """Many-to-many dependency: blocker must complete before blocked can start."""

    blocker_task_id: UUID
    blocked_task_id: UUID

    @model_validator(mode="after")
    def _no_self_dependency(self) -> TaskDependency:
        if self.blocker_task_id == self.blocked_task_id:
            raise ValueError("A task cannot depend on itself")
        return self
