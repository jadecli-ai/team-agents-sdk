"""Claude Agent SDK hooks for activity, cost, context, and cache management.

depends_on:
  - src/hooks/activity_tracker.py
  - src/hooks/cost_tracker.py
  - src/hooks/context_manager.py
  - src/hooks/tool_chain.py
  - src/cache/tool_cache.py
  - src/cache/compose.py
depended_by:
  - tests/test_hooks.py
  - tests/test_cache.py
semver: minor
"""

from src.cache.compose import compose_hooks
from src.cache.tool_cache import check_cache, get_cache_hooks, get_cache_stats
from src.hooks.activity_tracker import get_activity_hooks
from src.hooks.context_manager import get_context_hooks, get_context_stats, reset_context_state
from src.hooks.cost_tracker import update_task_cost_from_result
from src.hooks.tool_chain import get_chain_hooks

__all__ = [
    "check_cache",
    "compose_hooks",
    "get_activity_hooks",
    "get_cache_hooks",
    "get_cache_stats",
    "get_chain_hooks",
    "get_context_hooks",
    "get_context_stats",
    "reset_context_state",
    "update_task_cost_from_result",
]
