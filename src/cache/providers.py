"""Multi-provider Redis/Dragonfly client with failover and health checks.

Supports 4 concurrent cloud providers + local Redis. All providers are
active simultaneously — writes fan out to all, reads use the fastest responder.

depends_on:
  - src/get_env.py
depended_by:
  - src/cache/dragonfly_client.py
  - tests/test_cache.py
semver: minor
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum

import redis.asyncio as aioredis

from src.get_env import env

logger = logging.getLogger(__name__)


class ProviderStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNCONFIGURED = "unconfigured"


@dataclass
class ProviderHealth:
    name: str
    status: ProviderStatus
    latency_ms: float = 0.0
    error: str = ""
    server_info: str = ""


@dataclass
class Provider:
    name: str
    env_key: str
    client: aioredis.Redis | None = None
    healthy: bool = False
    latency_ms: float = float("inf")
    last_check: float = 0.0


# ── Provider Registry ──────────────────────────────────────────────────

PROVIDERS: list[dict] = [
    {"name": "upstash", "env_key": "PRJ_UPSTASH_REDIS_URL"},
    {"name": "redis-cloud", "env_key": "PRJ_REDIS_CLOUD_URL"},
    {"name": "dragonfly-cloud", "env_key": "PRJ_DRAGONFLY_CLOUD_URL"},
    {"name": "aiven", "env_key": "PRJ_AIVEN_DRAGONFLY_URL"},
    {"name": "local", "env_key": "PRJ_DRAGONFLY_URL"},
]

_providers: list[Provider] = []
_initialized = False


def _create_client(url: str) -> aioredis.Redis:
    """Create an async Redis client from URL."""
    return aioredis.from_url(
        url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=2,
        retry_on_timeout=False,
    )


def _init_providers() -> list[Provider]:
    """Initialize all configured providers."""
    global _providers, _initialized
    if _initialized:
        return _providers

    _providers = []
    for spec in PROVIDERS:
        url = env(spec["env_key"], default=None)
        if url:
            try:
                client = _create_client(url)
                _providers.append(
                    Provider(name=spec["name"], env_key=spec["env_key"], client=client)
                )
                logger.debug("Provider %s configured: %s", spec["name"], url.split("@")[-1])
            except Exception as e:
                logger.warning("Provider %s config error: %s", spec["name"], e)
        else:
            logger.debug("Provider %s not configured (%s not set)", spec["name"], spec["env_key"])

    _initialized = True
    return _providers


async def health_check_provider(provider: Provider) -> ProviderHealth:
    """PING a single provider and measure latency."""
    if not provider.client:
        return ProviderHealth(
            name=provider.name, status=ProviderStatus.UNCONFIGURED
        )

    start = time.monotonic()
    try:
        pong = await asyncio.wait_for(provider.client.ping(), timeout=3.0)
        latency = (time.monotonic() - start) * 1000
        provider.latency_ms = latency
        provider.healthy = True
        provider.last_check = time.monotonic()

        # Get server info for diagnostics
        try:
            info = await asyncio.wait_for(provider.client.info("server"), timeout=3.0)
            server_ver = info.get("redis_version", "unknown")
            server_info = f"v{server_ver}"
        except Exception:
            server_info = "connected"

        status = ProviderStatus.HEALTHY if latency < 500 else ProviderStatus.DEGRADED
        return ProviderHealth(
            name=provider.name,
            status=status,
            latency_ms=round(latency, 2),
            server_info=server_info,
        )
    except Exception as e:
        latency = (time.monotonic() - start) * 1000
        provider.healthy = False
        provider.latency_ms = float("inf")
        return ProviderHealth(
            name=provider.name,
            status=ProviderStatus.DOWN,
            latency_ms=round(latency, 2),
            error=str(e),
        )


async def health_check_all() -> list[ProviderHealth]:
    """Health check all configured providers concurrently."""
    providers = _init_providers()
    if not providers:
        return []

    results = await asyncio.gather(
        *(health_check_provider(p) for p in providers),
        return_exceptions=True,
    )

    health_list = []
    for r in results:
        if isinstance(r, Exception):
            health_list.append(
                ProviderHealth(name="unknown", status=ProviderStatus.DOWN, error=str(r))
            )
        else:
            health_list.append(r)

    return health_list


def get_fastest_healthy() -> Provider | None:
    """Return the fastest healthy provider, or None."""
    providers = _init_providers()
    healthy = [p for p in providers if p.healthy and p.client]
    if not healthy:
        return None
    return min(healthy, key=lambda p: p.latency_ms)


def get_all_healthy() -> list[Provider]:
    """Return all healthy providers (for fan-out writes)."""
    providers = _init_providers()
    return [p for p in providers if p.healthy and p.client]


def get_provider_by_name(name: str) -> Provider | None:
    """Get a specific provider by name."""
    providers = _init_providers()
    for p in providers:
        if p.name == name:
            return p
    return None


async def close_all() -> None:
    """Close all provider connections."""
    global _initialized
    for p in _providers:
        if p.client:
            try:
                await p.client.aclose()
            except Exception:
                pass
            p.client = None
            p.healthy = False
    _initialized = False
    _providers.clear()


def reset_providers() -> None:
    """Reset state without closing (for tests)."""
    global _initialized
    _providers.clear()
    _initialized = False
