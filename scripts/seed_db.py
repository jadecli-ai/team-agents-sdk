"""Seed sample data into Neon Postgres."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy as sa

from src.db.engine import get_session_factory, dispose_engine
from src.db.tables import tasks, subtasks, agent_activity


async def seed():
    factory = get_session_factory()

    # Create sample tasks
    task1_id = uuid4()
    task2_id = uuid4()
    task3_id = uuid4()

    async with factory() as session:
        await session.execute(
            sa.insert(tasks).values(
                [
                    {
                        "id": task1_id,
                        "title": "Review authentication module",
                        "description": "Full code review of auth.py including JWT handling",
                        "status": "completed",
                        "priority": "high",
                        "assigned_agent": "code_reviewer",
                        "estimated_cost_usd": 0.50,
                        "actual_cost_usd": 0.42,
                        "started_at": datetime(2025, 1, 15, 10, 0, tzinfo=timezone.utc),
                        "completed_at": datetime(2025, 1, 15, 10, 30, tzinfo=timezone.utc),
                    },
                    {
                        "id": task2_id,
                        "title": "Write integration tests for API",
                        "description": "Cover all REST endpoints with pytest",
                        "status": "in_progress",
                        "priority": "medium",
                        "assigned_agent": "test_runner",
                        "estimated_cost_usd": 1.00,
                        "actual_cost_usd": 0.15,
                        "started_at": datetime(2025, 1, 15, 11, 0, tzinfo=timezone.utc),
                    },
                    {
                        "id": task3_id,
                        "title": "Research caching strategies",
                        "description": "Evaluate Redis vs in-memory caching for crawl results",
                        "status": "pending",
                        "priority": "low",
                        "assigned_agent": "research_analyst",
                        "estimated_cost_usd": 0.30,
                    },
                ]
            )
        )

        # Sample subtask
        await session.execute(
            sa.insert(subtasks).values(
                parent_task_id=task1_id,
                subtask_type="git_hook",
                title="GitHub sync: issue #1",
                status="completed",
                output_summary="Synced to jadecli/team-agents-sdk#1",
                github_issue_number=1,
            )
        )

        # Sample agent activity
        await session.execute(
            sa.insert(agent_activity).values(
                [
                    {
                        "task_id": task1_id,
                        "agent_name": "code-reviewer",
                        "agent_role": "code_reviewer",
                        "hook_event": "PreToolUse",
                        "tool_name": "Read",
                        "tool_input_summary": '{"file_path": "src/auth.py"}',
                    },
                    {
                        "task_id": task1_id,
                        "agent_name": "code-reviewer",
                        "agent_role": "code_reviewer",
                        "hook_event": "PostToolUse",
                        "tool_name": "Read",
                        "duration_ms": 150,
                    },
                    {
                        "task_id": task1_id,
                        "agent_name": "code-reviewer",
                        "agent_role": "code_reviewer",
                        "hook_event": "Stop",
                        "num_turns": 8,
                        "cost_usd": 0.42,
                    },
                ]
            )
        )

        await session.commit()

    print(f"Seeded 3 tasks, 1 subtask, 3 activity events")
    await dispose_engine()


if __name__ == "__main__":
    asyncio.run(seed())
