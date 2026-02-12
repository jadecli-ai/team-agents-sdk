"""Tests for activity, cost, context, and chain hooks using mocks."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.cache.compose import compose_hooks
from src.cache.tool_cache import get_cache_hooks, get_cache_stats, reset_cache_stats
from src.hooks.activity_tracker import get_activity_hooks
from src.hooks.context_manager import (
    ContextState,
    get_context_hooks,
    get_context_stats,
    reset_context_state,
)
from src.hooks.cost_tracker import update_task_cost_from_result
from src.hooks.tool_chain import (
    clear_chains,
    get_chain,
    get_chain_hooks,
    list_chains,
    register_chain,
)


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


class TestContextState:
    def setup_method(self):
        reset_context_state()

    def test_reset(self):
        stats = get_context_stats()
        assert stats["total_output_bytes"] == 0
        assert stats["tool_call_count"] == 0
        assert stats["summarization_requested"] is False
        assert stats["pressure_pct"] == 0.0

    def test_default_thresholds(self):
        state = ContextState()
        assert state.OUTPUT_WARN_BYTES == 50_000
        assert state.OUTPUT_PRUNE_BYTES == 150_000
        assert state.MAX_TOOL_CALLS == 25


class TestContextHooks:
    def setup_method(self):
        reset_context_state()

    async def test_post_tool_increments_counters(self):
        hooks = get_context_hooks()
        await hooks["PostToolUse"]("Read", {"file_path": "/t.py"}, "x" * 100)
        stats = get_context_stats()
        assert stats["total_output_bytes"] == 100
        assert stats["tool_call_count"] == 1

    async def test_threshold_detection(self):
        hooks = get_context_hooks()
        # Accumulate over prune threshold
        for _ in range(4):
            await hooks["PostToolUse"]("Read", {}, "x" * 40_000)
        stats = get_context_stats()
        assert stats["summarization_requested"] is True
        assert stats["total_output_bytes"] == 160_000

    async def test_tool_call_limit_triggers_summarization(self):
        hooks = get_context_hooks()
        for i in range(25):
            await hooks["PostToolUse"]("Glob", {}, "file.py")
        stats = get_context_stats()
        assert stats["summarization_requested"] is True
        assert stats["tool_call_count"] == 25

    async def test_pre_tool_fires_advisory(self):
        """PreToolUse doesn't raise, even under pressure."""
        hooks = get_context_hooks()
        # Push past threshold
        for _ in range(4):
            await hooks["PostToolUse"]("Read", {}, "x" * 40_000)
        # Should not raise
        await hooks["PreToolUse"]("Read", {"file_path": "/t.py"})

    async def test_none_response_handled(self):
        hooks = get_context_hooks()
        await hooks["PostToolUse"]("Read", {}, None)
        stats = get_context_stats()
        assert stats["total_output_bytes"] == 0
        assert stats["tool_call_count"] == 1


class TestContextStats:
    def setup_method(self):
        reset_context_state()

    async def test_pressure_calculation(self):
        hooks = get_context_hooks()
        await hooks["PostToolUse"]("Read", {}, "x" * 75_000)
        stats = get_context_stats()
        assert stats["pressure_pct"] == 50.0

    async def test_pressure_at_zero(self):
        stats = get_context_stats()
        assert stats["pressure_pct"] == 0.0


class TestChainRegistry:
    def setup_method(self):
        clear_chains()

    def test_register_and_lookup(self):
        async def my_chain():
            return "result"

        register_chain("test_chain", my_chain)
        assert get_chain("test_chain") is my_chain

    def test_missing_chain_returns_none(self):
        assert get_chain("nonexistent") is None

    def test_list_chains(self):
        async def chain_a():
            return "a"

        async def chain_b():
            return "b"

        register_chain("alpha", chain_a)
        register_chain("beta", chain_b)
        assert sorted(list_chains()) == ["alpha", "beta"]

    def test_clear_chains(self):
        async def fn():
            return ""

        register_chain("temp", fn)
        clear_chains()
        assert list_chains() == []


class TestChainDetector:
    async def test_glob_result_detected(self):
        """Chain detector doesn't raise on Glob results."""
        hooks = get_chain_hooks()
        await hooks["PostToolUse"]("Glob", {}, "file1.py\nfile2.py\nfile3.py")

    async def test_non_glob_ignored(self):
        """Non-Glob tools don't trigger detection."""
        hooks = get_chain_hooks()
        await hooks["PostToolUse"]("Read", {}, "file contents")

    async def test_empty_result_handled(self):
        hooks = get_chain_hooks()
        await hooks["PostToolUse"]("Glob", {}, "")


# ── Composed Hooks Integration Tests ────────────────────────────────────


class TestComposeWithAllHooks:
    """Verify compose_hooks works end-to-end with activity + context + chain hooks."""

    def setup_method(self):
        reset_context_state()
        clear_chains()

    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_all_post_tool_use_handlers_fire(self, mock_factory):
        """Activity, context, and chain PostToolUse all execute via composed hook."""
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = MagicMock(return_value=session)

        composed = compose_hooks(
            get_activity_hooks(task_id=uuid4(), agent_name="test"),
            get_context_hooks(),
            get_chain_hooks(),
        )

        await composed["PostToolUse"]("Read", {"file_path": "/t.py"}, "hello world")

        # Activity tracker wrote to DB
        session.execute.assert_called()
        # Context manager tracked the output
        stats = get_context_stats()
        assert stats["tool_call_count"] == 1
        assert stats["total_output_bytes"] == len("hello world")

    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_context_state_accumulates_across_composed_calls(self, mock_factory):
        """Multiple calls through composed hooks accumulate context state."""
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = MagicMock(return_value=session)

        composed = compose_hooks(
            get_activity_hooks(task_id=uuid4(), agent_name="test"),
            get_context_hooks(),
            get_chain_hooks(),
        )

        for _ in range(3):
            await composed["PostToolUse"]("Read", {"file_path": "/t.py"}, "x" * 1000)

        stats = get_context_stats()
        assert stats["tool_call_count"] == 3
        assert stats["total_output_bytes"] == 3000

    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_activity_failure_does_not_block_context(self, mock_factory):
        """If activity tracker DB fails, context + chain hooks still run."""
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        session.execute.side_effect = RuntimeError("DB down")
        mock_factory.return_value = MagicMock(return_value=session)

        composed = compose_hooks(
            get_activity_hooks(task_id=uuid4(), agent_name="test"),
            get_context_hooks(),
            get_chain_hooks(),
        )

        # Should not raise despite DB failure
        await composed["PostToolUse"]("Glob", {}, "file1.py\nfile2.py")

        # Context hooks still fired
        stats = get_context_stats()
        assert stats["tool_call_count"] == 1

    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_pre_tool_use_fires_both_activity_and_context(self, mock_factory):
        """PreToolUse from activity + context both execute in composed hook."""
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = MagicMock(return_value=session)

        composed = compose_hooks(
            get_activity_hooks(task_id=uuid4(), agent_name="test"),
            get_context_hooks(),
            get_chain_hooks(),
        )

        # Both activity PreToolUse and context PreToolUse should fire
        await composed["PreToolUse"]("Read", {"file_path": "/t.py"})

        # Activity tracker logged the event
        session.execute.assert_called_once()


class TestComposeWithCacheHooks:
    """Verify compose_hooks works with all 4 hook types: activity + context + chain + cache."""

    def setup_method(self):
        reset_context_state()
        clear_chains()
        reset_cache_stats()

    @patch("src.cache.tool_cache.get_dragonfly")
    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_post_tool_use_fires_all_four(self, mock_factory, mock_get_df):
        """All 4 PostToolUse handlers fire for a cacheable tool."""
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = MagicMock(return_value=session)

        client = AsyncMock()
        client.set = AsyncMock()
        mock_get_df.return_value = client

        composed = compose_hooks(
            get_activity_hooks(task_id=uuid4(), agent_name="test"),
            get_context_hooks(),
            get_chain_hooks(),
            get_cache_hooks(),
        )

        await composed["PostToolUse"]("Read", {"file_path": "/t.py"}, "content")

        # Activity: DB insert
        session.execute.assert_called()
        # Context: tracked
        assert get_context_stats()["tool_call_count"] == 1
        # Cache: set called
        client.set.assert_called_once()
        assert get_cache_stats()["sets"] == 1

    @patch("src.cache.tool_cache.get_dragonfly")
    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_pre_tool_use_fires_context_advisor(self, mock_factory, mock_get_df):
        """PreToolUse from activity + context fires even with cache hooks composed."""
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = MagicMock(return_value=session)

        client = AsyncMock()
        mock_get_df.return_value = client

        composed = compose_hooks(
            get_activity_hooks(task_id=uuid4(), agent_name="test"),
            get_context_hooks(),
            get_chain_hooks(),
            get_cache_hooks(),
        )

        await composed["PreToolUse"]("Read", {"file_path": "/t.py"})

        # Activity tracker logged PreToolUse
        session.execute.assert_called_once()

    @patch("src.cache.tool_cache.get_dragonfly")
    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_cache_receives_set_for_cacheable_tool(self, mock_factory, mock_get_df):
        """Cache PostToolUse stores result for cacheable tools."""
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = MagicMock(return_value=session)

        client = AsyncMock()
        client.set = AsyncMock()
        mock_get_df.return_value = client

        composed = compose_hooks(
            get_activity_hooks(task_id=uuid4(), agent_name="test"),
            get_context_hooks(),
            get_chain_hooks(),
            get_cache_hooks(),
        )

        await composed["PostToolUse"]("Grep", {"pattern": "foo"}, "match line 1")

        # Redis set was called for the cacheable Grep result
        client.set.assert_called_once()

    @patch("src.cache.tool_cache.get_dragonfly")
    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_non_cacheable_skips_cache_but_fires_others(self, mock_factory, mock_get_df):
        """Bash tool skips cache but activity + context + chain still fire."""
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = MagicMock(return_value=session)

        client = AsyncMock()
        mock_get_df.return_value = client

        composed = compose_hooks(
            get_activity_hooks(task_id=uuid4(), agent_name="test"),
            get_context_hooks(),
            get_chain_hooks(),
            get_cache_hooks(),
        )

        await composed["PostToolUse"]("Bash", {"command": "ls"}, "output")

        # Activity still logged
        session.execute.assert_called()
        # Context still tracked
        assert get_context_stats()["tool_call_count"] == 1
        # Cache was NOT called (Bash is non-cacheable)
        client.set.assert_not_called()


class TestEndToEndWorkflow:
    """Simulate a realistic multi-tool agent turn through composed hooks."""

    def setup_method(self):
        reset_context_state()
        clear_chains()
        reset_cache_stats()

    @patch("src.cache.tool_cache.get_dragonfly")
    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_multi_tool_turn(self, mock_factory, mock_get_df):
        """Simulate: Read (cache miss) -> Grep (cache hit) -> verify state."""
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = MagicMock(return_value=session)

        client = AsyncMock()
        client.set = AsyncMock()
        client.get = AsyncMock(return_value=None)  # Start with cache miss
        mock_get_df.return_value = client

        composed = compose_hooks(
            get_activity_hooks(task_id=uuid4(), agent_name="coder"),
            get_context_hooks(),
            get_chain_hooks(),
            get_cache_hooks(),
        )

        # Step 1: Read tool — cache miss -> execute -> PostToolUse caches result
        await composed["PreToolUse"]("Read", {"file_path": "/src/main.py"})
        await composed["PostToolUse"]("Read", {"file_path": "/src/main.py"}, "def main(): pass")

        assert get_context_stats()["tool_call_count"] == 1
        assert get_cache_stats()["sets"] == 1

        # Step 2: Grep tool — PostToolUse caches result too
        await composed["PreToolUse"]("Grep", {"pattern": "main"})
        await composed["PostToolUse"]("Grep", {"pattern": "main"}, "main.py:1:def main(): pass")

        assert get_context_stats()["tool_call_count"] == 2
        assert get_cache_stats()["sets"] == 2

    @patch("src.cache.tool_cache.get_dragonfly")
    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_context_summarization_after_many_calls(self, mock_factory, mock_get_df):
        """After 25+ tool calls, context flags summarization_requested."""
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = MagicMock(return_value=session)

        client = AsyncMock()
        client.set = AsyncMock()
        mock_get_df.return_value = client

        composed = compose_hooks(
            get_activity_hooks(task_id=uuid4(), agent_name="coder"),
            get_context_hooks(),
            get_chain_hooks(),
            get_cache_hooks(),
        )

        # Accumulate 25 tool calls
        for i in range(25):
            await composed["PostToolUse"]("Read", {"file_path": f"/f{i}.py"}, "content")

        stats = get_context_stats()
        assert stats["summarization_requested"] is True
        assert stats["tool_call_count"] == 25

    @patch("src.cache.tool_cache.get_dragonfly")
    @patch("src.hooks.activity_tracker.get_session_factory")
    async def test_reset_state_cleans_slate(self, mock_factory, mock_get_df):
        """After reset, all state is clean."""
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = MagicMock(return_value=session)

        client = AsyncMock()
        client.set = AsyncMock()
        mock_get_df.return_value = client

        composed = compose_hooks(
            get_activity_hooks(task_id=uuid4(), agent_name="coder"),
            get_context_hooks(),
            get_chain_hooks(),
            get_cache_hooks(),
        )

        # Accumulate some state
        for i in range(5):
            await composed["PostToolUse"]("Read", {"file_path": f"/f{i}.py"}, "x" * 1000)

        assert get_context_stats()["tool_call_count"] == 5
        assert get_cache_stats()["sets"] == 5

        # Reset
        reset_context_state()
        reset_cache_stats()
        clear_chains()

        # Verify clean slate
        assert get_context_stats()["tool_call_count"] == 0
        assert get_context_stats()["total_output_bytes"] == 0
        assert get_context_stats()["summarization_requested"] is False
        assert get_cache_stats()["sets"] == 0
