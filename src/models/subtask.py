"""Subtask model matching semantic/subtasks.yaml.

schema: subtasks
depends_on:
  - src/models/base.py
  - src/models/enums.py
depended_by:
  - src/models/__init__.py
  - src/db/tables.py
  - tests/test_models.py
semver: minor
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from src.models.base import BaseEntity
from src.models.enums import SubtaskType, TaskStatus


class Subtask(BaseEntity):
    """A child task with type discriminator for git hooks and agent hooks."""

    parent_task_id: UUID
    subtask_type: SubtaskType
    title: str = Field(..., min_length=1, max_length=200)
    status: TaskStatus = TaskStatus.pending
    output_summary: str | None = None

    # git_hook specific
    github_issue_number: int | None = Field(default=None, ge=1)
    github_project_item_id: str | None = Field(default=None, max_length=50)

    # agent_hook specific
    agent_activity_id: UUID | None = None
