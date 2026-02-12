"""Async Dragonfly/Redis singleton client with multi-provider support.

Follows src/db/engine.py:get_engine() singleton pattern.
Handles rediss:// (SSL) automatically via redis-py.
Uses the fastest healthy provider from the multi-provider registry.

depends_on:
  - src/get_env.py
  - src/cache/providers.py
depended_by:
  - src/cache/tool_cache.py
  - src/cache/__init__.py
  - tests/test_cache.py
semver: minor
"""

from __future__ import annotations

import logging

import redis.asyncio as aioredis

from src.get_env import env

logger = logging.getLogger(__name__)

_client: aioredis.Redis | None = None

_DEFAULT_URL = "redis://localhost:6379/0"


def get_dragonfly() -> aioredis.Redis:
    """Get or create the async Redis/Dragonfly singleton.

    Tries the fastest healthy provider first (if providers are initialized).
    Falls back to PRJ_DRAGONFLY_URL or localhost.
    """
    global _client
    if _client is None:
        # Try multi-provider fastest-healthy first
        try:
            from src.cache.providers import get_fastest_healthy

            fastest = get_fastest_healthy()
            if fastest and fastest.client:
                _client = fastest.client
                logger.debug("Using provider %s (%.1fms)", fastest.name, fastest.latency_ms)
                return _client
        except Exception:
            pass  # providers not initialized yet, fall through

        # Fallback to single URL
        url = env("PRJ_DRAGONFLY_URL", default=_DEFAULT_URL)
        _client = aioredis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=10,
            socket_timeout=2,
            retry_on_timeout=False,
        )
        logger.debug("Dragonfly client created (fallback): %s", url.split("@")[-1])
    return _client


async def close_dragonfly() -> None:
    """Close the client and reset the singleton."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
        logger.debug("Dragonfly client closed")


def reset_dragonfly() -> None:
    """Reset the singleton without closing (for tests)."""
    global _client
    _client = None
