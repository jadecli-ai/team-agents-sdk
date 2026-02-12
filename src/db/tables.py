"""SQLAlchemy Table objects matching semantic YAML schemas.

schema: tasks, subtasks, task_dependencies, agent_activity
depends_on:
  - semantic/tasks.yaml
  - semantic/subtasks.yaml
  - semantic/task_dependencies.yaml
  - semantic/agent_activity.yaml
depended_by:
  - src/db/crud.py
  - src/db/__init__.py
  - src/hooks/activity_tracker.py
  - src/hooks/cost_tracker.py
  - tests/test_db.py
semver: major
"""

from __future__ import annotations

import sqlalchemy as sa

metadata = sa.MetaData()

tasks = sa.Table(
    "tasks",
    metadata,
    sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    sa.Column("title", sa.String(200), nullable=False),
    sa.Column("description", sa.Text, nullable=True),
    sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
    sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
    sa.Column("assigned_agent", sa.String(30), nullable=True),
    sa.Column("session_id", sa.String(100), nullable=True),
    sa.Column("estimated_cost_usd", sa.Float, nullable=False, server_default="0.0"),
    sa.Column("actual_cost_usd", sa.Float, nullable=False, server_default="0.0"),
    sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("github_issue_number", sa.Integer, nullable=True),
    sa.Column("github_project_item_id", sa.String(50), nullable=True),
    sa.Column("schema_version", sa.Integer, nullable=False, server_default="1"),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    ),
    sa.Index("ix_tasks_status", "status"),
    sa.Index("ix_tasks_priority", "priority"),
    sa.Index("ix_tasks_assigned_agent", "assigned_agent"),
)

subtasks = sa.Table(
    "subtasks",
    metadata,
    sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    sa.Column(
        "parent_task_id",
        sa.UUID,
        sa.ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("subtask_type", sa.String(20), nullable=False),
    sa.Column("title", sa.String(200), nullable=False),
    sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
    sa.Column("output_summary", sa.Text, nullable=True),
    sa.Column("github_issue_number", sa.Integer, nullable=True),
    sa.Column("github_project_item_id", sa.String(50), nullable=True),
    sa.Column(
        "agent_activity_id",
        sa.UUID,
        sa.ForeignKey("agent_activity.id", ondelete="SET NULL"),
        nullable=True,
    ),
    sa.Column("schema_version", sa.Integer, nullable=False, server_default="1"),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    ),
    sa.Index("ix_subtasks_parent_task_id", "parent_task_id"),
    sa.Index("ix_subtasks_subtask_type", "subtask_type"),
    sa.Index("ix_subtasks_status", "status"),
)

task_dependencies = sa.Table(
    "task_dependencies",
    metadata,
    sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    sa.Column(
        "blocker_task_id",
        sa.UUID,
        sa.ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "blocked_task_id",
        sa.UUID,
        sa.ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    ),
    sa.CheckConstraint(
        "blocker_task_id != blocked_task_id",
        name="ck_no_self_dependency",
    ),
    sa.UniqueConstraint("blocker_task_id", "blocked_task_id", name="uq_dependency"),
    sa.Index("ix_task_dependencies_blocker", "blocker_task_id"),
    sa.Index("ix_task_dependencies_blocked", "blocked_task_id"),
)

agent_activity = sa.Table(
    "agent_activity",
    metadata,
    sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
    sa.Column(
        "task_id",
        sa.UUID,
        sa.ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
    ),
    sa.Column(
        "subtask_id",
        sa.UUID,
        sa.ForeignKey("subtasks.id", ondelete="SET NULL"),
        nullable=True,
    ),
    sa.Column("agent_name", sa.String(50), nullable=False),
    sa.Column("agent_role", sa.String(30), nullable=True),
    sa.Column("session_id", sa.String(100), nullable=True),
    sa.Column("hook_event", sa.String(20), nullable=False),
    sa.Column("tool_name", sa.String(50), nullable=True),
    sa.Column("tool_input_summary", sa.String(2000), nullable=True),
    sa.Column("tool_response_summary", sa.String(2000), nullable=True),
    sa.Column("duration_ms", sa.Integer, nullable=True),
    sa.Column("cost_usd", sa.Float, nullable=True),
    sa.Column("num_turns", sa.Integer, nullable=True),
    sa.Column(
        "event_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    ),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    ),
    sa.Index("ix_agent_activity_task_id", "task_id"),
    sa.Index("ix_agent_activity_agent_name", "agent_name"),
    sa.Index("ix_agent_activity_hook_event", "hook_event"),
    sa.Index("ix_agent_activity_event_at", "event_at"),
)
