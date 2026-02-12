"""Tests for Pydantic models — validators, enum constraints, cross-field checks."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.models import (
    AgentActivity,
    Subtask,
    Task,
    TaskDependency,
    TaskPriority,
    TaskStatus,
    SubtaskType,
    AgentRole,
)


# ── Task ──────────────────────────────────────────────────────────────


class TestTask:
    def test_create_minimal(self):
        t = Task(title="Review auth module")
        assert t.title == "Review auth module"
        assert t.status == "pending"
        assert t.priority == "medium"
        assert t.actual_cost_usd == 0.0

    def test_title_cannot_be_blank(self):
        with pytest.raises(ValueError):
            Task(title="")

    def test_title_stripped(self):
        t = Task(title="  Fix bug  ")
        assert t.title == "Fix bug"

    def test_negative_cost_rejected(self):
        with pytest.raises(ValueError):
            Task(title="test", estimated_cost_usd=-1.0)

    def test_completed_requires_completed_at(self):
        with pytest.raises(ValueError, match="completed_at"):
            Task(title="test", status=TaskStatus.completed)

    def test_completed_with_timestamp_ok(self):
        t = Task(
            title="test",
            status=TaskStatus.completed,
            completed_at=datetime.now(timezone.utc),
        )
        assert t.status == "completed"

    def test_in_progress_requires_started_at(self):
        with pytest.raises(ValueError, match="started_at"):
            Task(title="test", status=TaskStatus.in_progress)

    def test_in_progress_with_started_ok(self):
        t = Task(
            title="test",
            status=TaskStatus.in_progress,
            started_at=datetime.now(timezone.utc),
        )
        assert t.status == "in_progress"

    def test_blocked_requires_blocker_ids(self):
        with pytest.raises(ValueError, match="blocker_id"):
            Task(title="test", status=TaskStatus.blocked)

    def test_blocked_with_blockers_ok(self):
        t = Task(
            title="test",
            status=TaskStatus.blocked,
            blocker_ids=[uuid4()],
        )
        assert t.status == "blocked"

    def test_enum_values_serialized(self):
        t = Task(title="test", priority=TaskPriority.critical)
        assert t.priority == "critical"

    def test_github_issue_number_ge_1(self):
        with pytest.raises(ValueError):
            Task(title="test", github_issue_number=0)

    def test_assigned_agent_enum(self):
        t = Task(title="test", assigned_agent=AgentRole.code_reviewer)
        assert t.assigned_agent == "code_reviewer"

    def test_from_attributes(self):
        """Simulate ORM row → model conversion."""

        class FakeRow:
            id = uuid4()
            title = "from ORM"
            description = None
            status = "pending"
            priority = "medium"
            assigned_agent = None
            session_id = None
            estimated_cost_usd = 0.0
            actual_cost_usd = 0.0
            started_at = None
            completed_at = None
            due_at = None
            github_issue_number = None
            github_project_item_id = None
            schema_version = 1
            created_at = datetime.now(timezone.utc)
            updated_at = datetime.now(timezone.utc)
            blocker_ids = []
            subtask_ids = []

        t = Task.model_validate(FakeRow())
        assert t.title == "from ORM"


# ── TaskDependency ────────────────────────────────────────────────────


class TestTaskDependency:
    def test_valid_dependency(self):
        a, b = uuid4(), uuid4()
        d = TaskDependency(blocker_task_id=a, blocked_task_id=b)
        assert d.blocker_task_id == a

    def test_self_dependency_rejected(self):
        same = uuid4()
        with pytest.raises(ValueError, match="itself"):
            TaskDependency(blocker_task_id=same, blocked_task_id=same)


# ── Subtask ───────────────────────────────────────────────────────────


class TestSubtask:
    def test_create_git_hook_subtask(self):
        s = Subtask(
            parent_task_id=uuid4(),
            subtask_type=SubtaskType.git_hook,
            title="Sync to GitHub",
        )
        assert s.subtask_type == "git_hook"
        assert s.status == "pending"

    def test_create_agent_hook_subtask(self):
        s = Subtask(
            parent_task_id=uuid4(),
            subtask_type=SubtaskType.agent_hook,
            title="Code review activity",
            agent_activity_id=uuid4(),
        )
        assert s.agent_activity_id is not None

    def test_title_cannot_be_blank(self):
        with pytest.raises(ValueError):
            Subtask(
                parent_task_id=uuid4(),
                subtask_type=SubtaskType.validation,
                title="",
            )


# ── AgentActivity ─────────────────────────────────────────────────────


class TestAgentActivity:
    def test_create_pre_tool_use(self):
        a = AgentActivity(
            agent_name="code-reviewer",
            hook_event="PreToolUse",
            tool_name="Read",
        )
        assert a.hook_event == "PreToolUse"

    def test_negative_duration_rejected(self):
        with pytest.raises(ValueError):
            AgentActivity(
                agent_name="test",
                hook_event="PostToolUse",
                duration_ms=-1,
            )

    def test_negative_cost_rejected(self):
        with pytest.raises(ValueError):
            AgentActivity(
                agent_name="test",
                hook_event="Stop",
                cost_usd=-0.5,
            )

    def test_agent_role_enum(self):
        a = AgentActivity(
            agent_name="lead",
            hook_event="Stop",
            agent_role=AgentRole.team_lead,
        )
        assert a.agent_role == "team_lead"
