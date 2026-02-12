"""Async Dragonfly/Redis singleton client.

Follows src/db/engine.py:get_engine() singleton pattern.
Handles rediss:// (SSL) automatically via redis-py.

depends_on:
  - src/get_env.py
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

    Uses PRJ_DRAGONFLY_URL from env (supports rediss:// for SSL).
    Falls back to redis://localhost:6379/0 for local dev.
    """
    global _client
    if _client is None:
        url = env("PRJ_DRAGONFLY_URL", default=_DEFAULT_URL)
        _client = aioredis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=10,  # cloud SSL handshake
            socket_timeout=2,  # fast fail on read/write
            retry_on_timeout=False,
        )
        logger.debug("Dragonfly client created: %s", url.split("@")[-1])
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
