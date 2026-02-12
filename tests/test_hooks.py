"""Tests for activity and cost tracker hooks using mocks."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.hooks.activity_tracker import get_activity_hooks
from src.hooks.cost_tracker import update_task_cost_from_result


@pytest.fixture
def mock_session():
    """Create a mock async session factory."""
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    factory = MagicMock(return_value=session)
    return factory, session


class TestActivityTracker:
    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_pre_tool_use_logs_event(self, mock_factory):
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = MagicMock(return_value=session)

        hooks = get_activity_hooks(task_id=uuid4(), agent_name="reviewer")
        await hooks["PreToolUse"]("Read", {"file_path": "/test.py"})

        session.execute.assert_called_once()
        session.commit.assert_called_once()

    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_post_tool_use_computes_duration(self, mock_factory):
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = MagicMock(return_value=session)

        hooks = get_activity_hooks(task_id=uuid4(), agent_name="reviewer")

        # PreToolUse records start time
        await hooks["PreToolUse"]("Read", {"file_path": "/test.py"})
        # PostToolUse computes duration
        await hooks["PostToolUse"]("Read", {"file_path": "/test.py"}, "file contents")

        assert session.execute.call_count == 2
        assert session.commit.call_count == 2

    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_stop_logs_event(self, mock_factory):
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = MagicMock(return_value=session)

        hooks = get_activity_hooks(task_id=uuid4(), agent_name="lead")
        await hooks["Stop"](num_turns=5, cost_usd=0.12)

        session.execute.assert_called_once()

    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_db_failure_does_not_raise(self, mock_factory):
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        session.execute.side_effect = RuntimeError("DB down")
        mock_factory.return_value = MagicMock(return_value=session)

        hooks = get_activity_hooks(task_id=uuid4(), agent_name="test")
        # Should not raise
        await hooks["PreToolUse"]("Read", {})


class TestCostTracker:
    @patch("src.db.crud.get_session_factory")
    async def test_updates_cost(self, mock_factory):
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = MagicMock(return_value=session)

        result = MagicMock()
        result.total_cost_usd = 0.05

        await update_task_cost_from_result(uuid4(), result)

        session.execute.assert_called_once()
        session.commit.assert_called_once()

    @patch("src.db.crud.get_session_factory")
    async def test_zero_cost_skipped(self, mock_factory):
        result = MagicMock()
        result.total_cost_usd = 0.0

        await update_task_cost_from_result(uuid4(), result)

        mock_factory.assert_not_called()

    @patch("src.db.crud.get_session_factory")
    async def test_none_cost_skipped(self, mock_factory):
        result = MagicMock()
        result.total_cost_usd = None

        await update_task_cost_from_result(uuid4(), result)

        mock_factory.assert_not_called()

    @patch("src.db.crud.get_session_factory")
    async def test_db_failure_does_not_raise(self, mock_factory):
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        session.execute.side_effect = RuntimeError("DB down")
        mock_factory.return_value = MagicMock(return_value=session)

        result = MagicMock()
        result.total_cost_usd = 0.05

        # Should not raise
        await update_task_cost_from_result(uuid4(), result)
