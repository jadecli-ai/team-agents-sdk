"""Core tool result caching with smart reference-passing.

Cache key: tc:{tool_name}:{sha256(json(sorted_input))[:16]}
Large results (>512KB) stored as ctx:task:<uuid> with a reference summary.

depends_on:
  - src/cache/dragonfly_client.py
depended_by:
  - src/cache/__init__.py
  - tests/test_cache.py
semver: minor
"""

from __future__ import annotations

import hashlib
import json
import logging
from uuid import uuid4

from src.cache.dragonfly_client import get_dragonfly

logger = logging.getLogger(__name__)

# ── TTL Policy ───────────────────────────────────────────────────────────

_TOOL_TTLS: dict[str, int] = {
    "Read": 300,
    "Grep": 300,
    "Glob": 300,
    "WebFetch": 900,
    "WebSearch": 900,
}

_NEVER_CACHE = frozenset(
    {
        "Bash",
        "Write",
        "Edit",
        "NotebookEdit",
        "Task",
        "SendMessage",
        "TaskCreate",
        "TaskUpdate",
        "TaskList",
        "TaskGet",
        "AskUserQuestion",
        "EnterPlanMode",
        "ExitPlanMode",
        "TeamCreate",
        "TeamDelete",
        "Skill",
    }
)

_CONTEXT_TTL = 3600  # 1 hour for large result references
_SIZE_THRESHOLD = 512 * 1024  # 512KB — above this, store by reference

# ── Stats ────────────────────────────────────────────────────────────────

_stats = {"hits": 0, "misses": 0, "sets": 0, "refs": 0, "errors": 0}


def _cache_key(tool_name: str, tool_input: dict) -> str:
    """Generate deterministic cache key from tool name and input."""
    payload = json.dumps(tool_input, sort_keys=True, default=str)
    digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
    return f"tc:{tool_name}:{digest}"


def is_cacheable(tool_name: str) -> bool:
    """Check if a tool's results should be cached."""
    return tool_name not in _NEVER_CACHE and tool_name in _TOOL_TTLS


async def check_cache(tool_name: str, tool_input: dict) -> str | None:
    """Check cache for a tool result. Returns None on miss or error."""
    if not is_cacheable(tool_name):
        return None

    try:
        client = get_dragonfly()
        key = _cache_key(tool_name, tool_input)
        result = await client.get(key)
        if result is not None:
            _stats["hits"] += 1
            logger.debug("Cache HIT: %s", key)
            return result
        _stats["misses"] += 1
        return None
    except Exception:
        _stats["errors"] += 1
        logger.debug("Cache check error for %s — returning None", tool_name, exc_info=True)
        return None


async def set_cache_smart(tool_name: str, tool_input: dict, result: str) -> str:
    """Cache a tool result. Large results stored by reference.

    Returns the result to pass to the agent (may be a reference summary
    for large results).
    """
    if not is_cacheable(tool_name):
        return result

    try:
        client = get_dragonfly()
        result_bytes = len(result.encode("utf-8"))

        if result_bytes > _SIZE_THRESHOLD:
            # Store full result by reference
            ref_key = f"ctx:task:{uuid4().hex[:12]}"
            await client.set(ref_key, result, ex=_CONTEXT_TTL)
            _stats["refs"] += 1
            _stats["sets"] += 1
            summary = (
                f"[REFERENCE PASSED] {result_bytes:,} bytes stored at {ref_key}. "
                f"First 200 chars: {result[:200]}"
            )
            # Also cache the summary under the tool cache key
            key = _cache_key(tool_name, tool_input)
            ttl = _TOOL_TTLS.get(tool_name, 300)
            await client.set(key, summary, ex=ttl)
            logger.info("Cache REF: %s -> %s (%d bytes)", key, ref_key, result_bytes)
            return summary
        else:
            key = _cache_key(tool_name, tool_input)
            ttl = _TOOL_TTLS.get(tool_name, 300)
            await client.set(key, result, ex=ttl)
            _stats["sets"] += 1
            logger.debug("Cache SET: %s (TTL=%ds, %d bytes)", key, ttl, result_bytes)
            return result
    except Exception:
        _stats["errors"] += 1
        logger.debug("Cache set error for %s — returning raw result", tool_name, exc_info=True)
        return result


def get_cache_hooks() -> dict:
    """Returns hooks that auto-populate cache on PostToolUse."""
    return {
        "PostToolUse": _auto_populate,
    }


async def _auto_populate(
    tool_name: str, tool_input: dict, tool_response: str | None = None, **_kwargs
) -> None:
    """Auto-populate cache after tool execution."""
    if tool_response and is_cacheable(tool_name):
        await set_cache_smart(tool_name, tool_input, tool_response)


def get_cache_stats() -> dict:
    """Return cache hit/miss/set/ref counters."""
    return dict(_stats)


def reset_cache_stats() -> None:
    """Reset stats counters (for tests)."""
    for key in _stats:
        _stats[key] = 0


async def flush_cache() -> int:
    """Delete all tc:* and ctx:* keys. Returns count of deleted keys."""
    try:
        client = get_dragonfly()
        count = 0
        for pattern in ("tc:*", "ctx:*"):
            async for key in client.scan_iter(match=pattern):
                await client.delete(key)
                count += 1
        logger.info("Cache flushed: %d keys deleted", count)
        return count
    except Exception:
        logger.exception("Cache flush error")
        return 0
