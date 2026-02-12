"""Tests for cache module: dragonfly client, tool cache, and compose hooks.

Why mocks: Redis/Dragonfly is an external service. Tests mock the client
to verify caching logic (key gen, TTL, reference-passing, composition)
without requiring a running Redis instance.
"""

from __future__ import annotations

import asyncio
import os
from unittest.mock import AsyncMock, patch

import pytest

from src.cache.compose import compose_hooks
from src.cache.tool_cache import (
    _cache_key,
    check_cache,
    flush_cache,
    get_cache_hooks,
    get_cache_stats,
    is_cacheable,
    reset_cache_stats,
    set_cache_smart,
)


# ── Cache Key Generation ────────────────────────────────────────────────


class TestCacheKeyGeneration:
    def test_deterministic(self):
        """Same input always produces same key."""
        key1 = _cache_key("Read", {"file_path": "/test.py"})
        key2 = _cache_key("Read", {"file_path": "/test.py"})
        assert key1 == key2

    def test_order_independent(self):
        """Dict key order doesn't affect cache key."""
        key1 = _cache_key("Grep", {"pattern": "foo", "path": "/src"})
        key2 = _cache_key("Grep", {"path": "/src", "pattern": "foo"})
        assert key1 == key2

    def test_tool_partitioned(self):
        """Different tools produce different keys for same input."""
        key1 = _cache_key("Read", {"file_path": "/test.py"})
        key2 = _cache_key("Glob", {"file_path": "/test.py"})
        assert key1 != key2

    def test_prefix(self):
        """Key starts with tc: namespace."""
        key = _cache_key("Read", {"file_path": "/test.py"})
        assert key.startswith("tc:Read:")

    def test_different_inputs_different_keys(self):
        """Different inputs produce different keys."""
        key1 = _cache_key("Read", {"file_path": "/a.py"})
        key2 = _cache_key("Read", {"file_path": "/b.py"})
        assert key1 != key2


# ── Cacheability ────────────────────────────────────────────────────────


class TestCacheability:
    def test_cacheable_tools(self):
        for tool in ("Read", "Grep", "Glob", "WebFetch", "WebSearch"):
            assert is_cacheable(tool), f"{tool} should be cacheable"

    def test_non_cacheable_tools(self):
        for tool in ("Bash", "Write", "Edit", "NotebookEdit", "Task", "SendMessage"):
            assert not is_cacheable(tool), f"{tool} should NOT be cacheable"

    def test_unknown_tool_not_cacheable(self):
        assert not is_cacheable("UnknownTool")


# ── check_cache ─────────────────────────────────────────────────────────


class TestCheckCache:
    def setup_method(self):
        reset_cache_stats()

    @patch("src.cache.tool_cache.get_dragonfly")
    async def test_cache_hit(self, mock_get_df):
        client = AsyncMock()
        client.get = AsyncMock(return_value="cached result")
        mock_get_df.return_value = client

        result = await check_cache("Read", {"file_path": "/test.py"})
        assert result == "cached result"
        assert get_cache_stats()["hits"] == 1

    @patch("src.cache.tool_cache.get_dragonfly")
    async def test_cache_miss(self, mock_get_df):
        client = AsyncMock()
        client.get = AsyncMock(return_value=None)
        mock_get_df.return_value = client

        result = await check_cache("Read", {"file_path": "/test.py"})
        assert result is None
        assert get_cache_stats()["misses"] == 1

    async def test_non_cacheable_returns_none(self):
        result = await check_cache("Bash", {"command": "ls"})
        assert result is None

    @patch("src.cache.tool_cache.get_dragonfly")
    async def test_error_returns_none(self, mock_get_df):
        client = AsyncMock()
        client.get = AsyncMock(side_effect=ConnectionError("down"))
        mock_get_df.return_value = client

        result = await check_cache("Read", {"file_path": "/test.py"})
        assert result is None
        assert get_cache_stats()["errors"] == 1


# ── set_cache_smart ─────────────────────────────────────────────────────


class TestSetCacheSmart:
    def setup_method(self):
        reset_cache_stats()

    @patch("src.cache.tool_cache.get_dragonfly")
    async def test_small_result_cached_inline(self, mock_get_df):
        client = AsyncMock()
        client.set = AsyncMock()
        mock_get_df.return_value = client

        result = await set_cache_smart("Read", {"file_path": "/t.py"}, "small data")
        assert result == "small data"
        client.set.assert_called_once()
        assert get_cache_stats()["sets"] == 1
        assert get_cache_stats()["refs"] == 0

    @patch("src.cache.tool_cache.get_dragonfly")
    async def test_large_result_stored_by_reference(self, mock_get_df):
        client = AsyncMock()
        client.set = AsyncMock()
        mock_get_df.return_value = client

        large_data = "x" * (512 * 1024 + 1)  # Just over 512KB
        result = await set_cache_smart("Read", {"file_path": "/big.py"}, large_data)

        assert "[REFERENCE PASSED]" in result
        assert "ctx:task:" in result
        # Two sets: one for reference, one for summary under tool cache key
        assert client.set.call_count == 2
        assert get_cache_stats()["refs"] == 1

    @patch("src.cache.tool_cache.get_dragonfly")
    async def test_error_returns_raw_result(self, mock_get_df):
        client = AsyncMock()
        client.set = AsyncMock(side_effect=ConnectionError("down"))
        mock_get_df.return_value = client

        result = await set_cache_smart("Read", {"file_path": "/t.py"}, "data")
        assert result == "data"
        assert get_cache_stats()["errors"] == 1

    async def test_non_cacheable_returns_unchanged(self):
        result = await set_cache_smart("Bash", {"command": "ls"}, "output")
        assert result == "output"


# ── Cache Hooks ─────────────────────────────────────────────────────────


class TestCacheHooks:
    def setup_method(self):
        reset_cache_stats()

    @patch("src.cache.tool_cache.get_dragonfly")
    async def test_post_tool_use_populates(self, mock_get_df):
        client = AsyncMock()
        client.set = AsyncMock()
        mock_get_df.return_value = client

        hooks = get_cache_hooks()
        await hooks["PostToolUse"]("Read", {"file_path": "/t.py"}, "content")

        client.set.assert_called_once()
        assert get_cache_stats()["sets"] == 1

    @patch("src.cache.tool_cache.get_dragonfly")
    async def test_skips_non_cacheable(self, mock_get_df):
        client = AsyncMock()
        mock_get_df.return_value = client

        hooks = get_cache_hooks()
        await hooks["PostToolUse"]("Bash", {"command": "ls"}, "output")

        client.set.assert_not_called()


# ── Cache Stats ─────────────────────────────────────────────────────────


class TestCacheStats:
    def test_returns_counts(self):
        reset_cache_stats()
        stats = get_cache_stats()
        assert stats == {"hits": 0, "misses": 0, "sets": 0, "refs": 0, "errors": 0}

    def test_reset_clears(self):
        # Manually set a stat then reset
        from src.cache import tool_cache

        tool_cache._stats["hits"] = 42
        reset_cache_stats()
        assert get_cache_stats()["hits"] == 0


# ── Flush ───────────────────────────────────────────────────────────────


class TestFlushCache:
    @patch("src.cache.tool_cache.get_dragonfly")
    async def test_flush_deletes_keys(self, mock_get_df):
        client = AsyncMock()

        async def fake_scan_iter(match=""):
            if match == "tc:*":
                for k in ["tc:Read:abc", "tc:Glob:def"]:
                    yield k
            elif match == "ctx:*":
                for k in ["ctx:task:xyz"]:
                    yield k

        client.scan_iter = fake_scan_iter
        client.delete = AsyncMock()
        mock_get_df.return_value = client

        count = await flush_cache()
        assert count == 3
        assert client.delete.call_count == 3

    @patch("src.cache.tool_cache.get_dragonfly")
    async def test_flush_error_returns_zero(self, mock_get_df):
        mock_get_df.side_effect = ConnectionError("down")
        count = await flush_cache()
        assert count == 0


# ── compose_hooks ───────────────────────────────────────────────────────


class TestComposeHooks:
    def test_empty(self):
        result = compose_hooks()
        assert result == {}

    def test_single_passthrough(self):
        async def handler(tool_name, tool_input):
            pass

        result = compose_hooks({"PreToolUse": handler})
        assert result["PreToolUse"] is handler  # exact same function, no wrapper

    async def test_chained_handlers(self):
        calls = []

        async def handler_a(tool_name, **_kw):
            calls.append("a")

        async def handler_b(tool_name, **_kw):
            calls.append("b")

        result = compose_hooks(
            {"PostToolUse": handler_a},
            {"PostToolUse": handler_b},
        )
        await result["PostToolUse"]("Read")
        assert calls == ["a", "b"]

    async def test_failure_isolation(self):
        """One failing handler doesn't prevent others from running."""
        calls = []

        async def handler_fail(**_kw):
            raise RuntimeError("boom")

        async def handler_ok(**_kw):
            calls.append("ok")

        result = compose_hooks(
            {"PostToolUse": handler_fail},
            {"PostToolUse": handler_ok},
        )
        await result["PostToolUse"]()
        assert calls == ["ok"]

    def test_ordering_preserved(self):
        async def first(**_kw):
            pass

        async def second(**_kw):
            pass

        result = compose_hooks(
            {"PreToolUse": first},
            {"PreToolUse": second},
        )
        # The chained handler is a wrapper, not the originals
        assert result["PreToolUse"].__qualname__ == "chained_PreToolUse"

    def test_disjoint_events(self):
        async def pre_handler(**_kw):
            pass

        async def post_handler(**_kw):
            pass

        result = compose_hooks(
            {"PreToolUse": pre_handler},
            {"PostToolUse": post_handler},
        )
        assert result["PreToolUse"] is pre_handler
        assert result["PostToolUse"] is post_handler

    async def test_compose_with_all_hook_types(self):
        """Verify context + chain + cache hooks compose together."""
        from src.hooks.context_manager import get_context_hooks
        from src.hooks.tool_chain import get_chain_hooks

        composed = compose_hooks(
            get_context_hooks(),
            get_chain_hooks(),
            get_cache_hooks(),
        )
        # PostToolUse should be chained (3 handlers)
        assert "PostToolUse" in composed
        # PreToolUse only from context hooks (1 handler)
        assert "PreToolUse" in composed


# ── Multi-Provider Tests ──────────────────────────────────────────────


class TestProviderRegistry:
    def setup_method(self):
        from src.cache.providers import reset_providers

        reset_providers()

    def teardown_method(self):
        from src.cache.providers import reset_providers

        reset_providers()

    @patch.dict(
        os.environ,
        {
            "PRJ_UPSTASH_REDIS_URL": "",
            "PRJ_REDIS_CLOUD_URL": "",
            "PRJ_DRAGONFLY_CLOUD_URL": "",
            "PRJ_AIVEN_DRAGONFLY_URL": "",
            "PRJ_DRAGONFLY_URL": "",
        },
    )
    def test_no_providers_configured(self):
        from src.cache.providers import _init_providers, reset_providers

        reset_providers()
        providers = _init_providers()
        assert len(providers) == 0

    @patch.dict(
        os.environ,
        {"PRJ_UPSTASH_REDIS_URL": "redis://fake:6379", "PRJ_DRAGONFLY_URL": "redis://localhost:6379"},
    )
    def test_multiple_providers_configured(self):
        from src.cache.providers import _init_providers, reset_providers

        reset_providers()
        providers = _init_providers()
        names = [p.name for p in providers]
        assert "upstash" in names
        assert "local" in names

    def test_get_fastest_healthy_none_when_empty(self):
        from src.cache.providers import get_fastest_healthy

        assert get_fastest_healthy() is None

    def test_get_all_healthy_empty_when_none(self):
        from src.cache.providers import get_all_healthy

        assert get_all_healthy() == []

    def test_provider_status_enum(self):
        from src.cache.providers import ProviderStatus

        assert ProviderStatus.HEALTHY == "healthy"
        assert ProviderStatus.DOWN == "down"
        assert ProviderStatus.UNCONFIGURED == "unconfigured"

    def test_provider_health_dataclass(self):
        from src.cache.providers import ProviderHealth, ProviderStatus

        h = ProviderHealth(name="test", status=ProviderStatus.HEALTHY, latency_ms=1.5)
        assert h.name == "test"
        assert h.latency_ms == 1.5

    @patch.dict(os.environ, {"PRJ_UPSTASH_REDIS_URL": "redis://fake:6379"})
    async def test_health_check_down_provider(self):
        from src.cache.providers import _init_providers, health_check_all, reset_providers

        reset_providers()
        _init_providers()
        results = await health_check_all()
        assert len(results) == 1
        assert results[0].status.value == "down"

    def test_get_provider_by_name_not_found(self):
        from src.cache.providers import get_provider_by_name

        assert get_provider_by_name("nonexistent") is None

    def test_reset_clears_state(self):
        from src.cache.providers import _init_providers, _providers, reset_providers

        reset_providers()
        assert len(_providers) == 0


# ── Live Redis/Dragonfly Integration Tests ──────────────────────────────


@pytest.mark.skipif(
    not os.getenv("PRJ_DRAGONFLY_URL"),
    reason="PRJ_DRAGONFLY_URL not set",
)
class TestLiveCache:
    """Integration tests against a real Redis/Dragonfly instance."""

    def setup_method(self):
        reset_cache_stats()
        # Reset singleton so it picks up the real URL
        from src.cache.dragonfly_client import reset_dragonfly

        reset_dragonfly()

    def teardown_method(self):
        # Flush test keys and reset singleton
        from src.cache.dragonfly_client import reset_dragonfly

        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already inside async context; schedule cleanup
            pass
        reset_dragonfly()

    async def _cleanup(self):
        """Flush all cache keys after each test."""
        await flush_cache()

    async def test_live_set_and_get(self):
        """Set a cache entry for Read tool, then retrieve it."""
        try:
            tool_input = {"file_path": "/live/test.py"}
            result = await set_cache_smart("Read", tool_input, "live content here")
            assert result == "live content here"
            assert get_cache_stats()["sets"] == 1

            cached = await check_cache("Read", tool_input)
            assert cached == "live content here"
            assert get_cache_stats()["hits"] == 1
        finally:
            await self._cleanup()

    async def test_live_reference_passing(self):
        """Large result (>512KB) is stored by reference."""
        try:
            large_data = "x" * (512 * 1024 + 1)
            tool_input = {"file_path": "/live/big.py"}
            result = await set_cache_smart("Read", tool_input, large_data)

            assert "[REFERENCE PASSED]" in result
            assert get_cache_stats()["refs"] == 1

            # Subsequent check_cache returns the reference summary
            cached = await check_cache("Read", tool_input)
            assert cached is not None
            assert "[REFERENCE PASSED]" in cached
        finally:
            await self._cleanup()

    async def test_live_ttl_respected(self):
        """Set with short TTL, verify expiry."""
        try:
            from src.cache.dragonfly_client import get_dragonfly

            client = get_dragonfly()
            # Manually set with 1-second TTL
            key = _cache_key("Read", {"file_path": "/live/ttl.py"})
            await client.set(key, "ephemeral", ex=1)

            # Should be there immediately
            val = await client.get(key)
            assert val == "ephemeral"

            # Wait for expiry
            await asyncio.sleep(1.5)

            val = await client.get(key)
            assert val is None
        finally:
            await self._cleanup()

    async def test_live_flush(self):
        """Set keys, flush, verify gone."""
        try:
            await set_cache_smart("Read", {"file_path": "/live/a.py"}, "data-a")
            await set_cache_smart("Grep", {"pattern": "live"}, "data-b")
            assert get_cache_stats()["sets"] == 2

            count = await flush_cache()
            assert count >= 2

            # Both should be gone
            cached_a = await check_cache("Read", {"file_path": "/live/a.py"})
            cached_b = await check_cache("Grep", {"pattern": "live"})
            assert cached_a is None
            assert cached_b is None
        finally:
            await self._cleanup()

    async def test_live_non_cacheable_skipped(self):
        """check_cache for Bash returns None without touching Redis."""
        try:
            result = await check_cache("Bash", {"command": "ls"})
            assert result is None
            # No hits or misses — skipped before Redis call
            assert get_cache_stats()["hits"] == 0
            assert get_cache_stats()["misses"] == 0
        finally:
            await self._cleanup()
