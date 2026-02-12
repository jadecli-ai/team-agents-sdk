"""Cache-first agent workflow — Cloud Hive.

Tier 2 working memory via Dragonfly/Redis with smart reference-passing
for large results. All cache operations are fire-and-forget.
Multi-provider support: Upstash, Redis Cloud, Dragonfly Cloud, Aiven, local.

schema: n/a
depends_on:
  - src/cache/dragonfly_client.py
  - src/cache/tool_cache.py
  - src/cache/compose.py
  - src/cache/providers.py
depended_by:
  - src/hooks/__init__.py
  - tests/test_cache.py
semver: minor
"""

from src.cache.compose import compose_hooks
from src.cache.dragonfly_client import get_dragonfly
from src.cache.providers import (
    ProviderHealth,
    ProviderStatus,
    close_all,
    get_all_healthy,
    get_fastest_healthy,
    get_provider_by_name,
    health_check_all,
    health_check_provider,
    reset_providers,
)
from src.cache.tool_cache import (
    check_cache,
    flush_cache,
    get_cache_hooks,
    get_cache_stats,
    set_cache_smart,
)

__all__ = [
    "ProviderHealth",
    "ProviderStatus",
    "check_cache",
    "close_all",
    "compose_hooks",
    "flush_cache",
    "get_all_healthy",
    "get_cache_hooks",
    "get_cache_stats",
    "get_dragonfly",
    "get_fastest_healthy",
    "get_provider_by_name",
    "health_check_all",
    "health_check_provider",
    "reset_providers",
    "set_cache_smart",
]
