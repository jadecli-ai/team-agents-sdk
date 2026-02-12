"""Database round-trip tests.

These tests require PRJ_NEON_DATABASE_URL to be set. Skip if not available.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
import sqlalchemy as sa

from src.models import Task, TaskStatus

# Skip entire module if no database URL
pytestmark = pytest.mark.skipif(
    not os.environ.get("PRJ_NEON_DATABASE_URL"),
    reason="PRJ_NEON_DATABASE_URL not set",
)


@pytest.fixture
async def session():
    from src.db.engine import get_session_factory, dispose_engine

    factory = get_session_factory()
    async with factory() as s:
        yield s
    await dispose_engine()


class TestDatabaseRoundTrip:
    async def test_insert_and_read_task(self, session):
        from src.db.tables import tasks

        task_id = uuid4()
        await session.execute(
            sa.insert(tasks).values(
                id=task_id,
                title="Test task",
                status="pending",
                priority="medium",
            )
        )
        await session.commit()

        row = (
            await session.execute(
                sa.select(tasks).where(tasks.c.id == task_id)
            )
        ).mappings().first()

        assert row is not None
        assert row["title"] == "Test task"
        assert row["status"] == "pending"

        # Cleanup
        await session.execute(sa.delete(tasks).where(tasks.c.id == task_id))
        await session.commit()

    async def test_insert_task_dependency(self, session):
        from src.db.tables import tasks, task_dependencies

        a_id, b_id = uuid4(), uuid4()
        await session.execute(
            sa.insert(tasks).values(
                [
                    {"id": a_id, "title": "Blocker", "status": "pending", "priority": "high"},
                    {"id": b_id, "title": "Blocked", "status": "blocked", "priority": "medium"},
                ]
            )
        )
        await session.execute(
            sa.insert(task_dependencies).values(
                blocker_task_id=a_id,
                blocked_task_id=b_id,
            )
        )
        await session.commit()

        row = (
            await session.execute(
                sa.select(task_dependencies).where(
                    task_dependencies.c.blocked_task_id == b_id
                )
            )
        ).mappings().first()

        assert row is not None
        assert row["blocker_task_id"] == a_id

        # Cleanup (cascade deletes dependencies)
        await session.execute(sa.delete(tasks).where(tasks.c.id.in_([a_id, b_id])))
        await session.commit()
