"""Cache-first agent workflow — Cloud Hive.

Tier 2 working memory via Dragonfly/Redis with smart reference-passing
for large results. All cache operations are fire-and-forget.

schema: n/a
depends_on:
  - src/cache/dragonfly_client.py
  - src/cache/tool_cache.py
  - src/cache/compose.py
depended_by:
  - src/hooks/__init__.py
  - tests/test_cache.py
semver: minor
"""

from src.cache.compose import compose_hooks
from src.cache.dragonfly_client import get_dragonfly
from src.cache.tool_cache import (
    check_cache,
    flush_cache,
    get_cache_hooks,
    get_cache_stats,
    set_cache_smart,
)

__all__ = [
    "check_cache",
    "compose_hooks",
    "flush_cache",
    "get_cache_hooks",
    "get_cache_stats",
    "get_dragonfly",
    "set_cache_smart",
]
