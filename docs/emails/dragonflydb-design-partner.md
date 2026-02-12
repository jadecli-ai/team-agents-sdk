To: info@dragonflydb.io
Subject: Design Partner Inquiry — Dragonfly as AI Agent Context Bus

Hi Dragonfly Team,

Congratulations on the CNCF graduation — well deserved.

I'm Jade, building JadeCLI, an open-source multi-agent system where AI agents share working memory through a Redis-compatible context bus. I'd like to explore a design partner arrangement.

## The Use Case

We run 5-8 Claude Code agents in parallel, each performing expensive operations (code analysis, web searches, file system scans). Our cache layer:

- **Deterministic cache keys**: `tc:{tool_name}:{sha256(input)[:16]}` — identical tool calls across agents resolve to the same key
- **Smart reference-passing**: Results over 512KB get stored as `ctx:task:<uuid>` — agents pass lightweight pointers instead of megabytes through their context windows
- **Fire-and-forget writes**: Cache operations never block the agent runtime
- **TTL-based eviction**: Read/Grep/Glob at 300s, WebFetch/WebSearch at 900s, context refs at 3600s

This is a **write-heavy, concurrent workload** — exactly where Dragonfly's multi-threaded design outperforms single-threaded Redis.

## What We'd Publish

In exchange for startup credits or an extended trial:

1. **Architecture blog post**: "Dragonfly as a Cognitive Bus for LLM Agents" — showing the cache-first pattern with benchmarks
2. **Open-source reference implementation**: Our `src/cache/` module is already MIT-licensed with 27 tests
3. **Performance comparison**: Local Redis 8 vs Dragonfly Cloud under concurrent agent load

## Current State

- 98 tests passing (27 cache-specific)
- Running on Redis 8 locally, ready to migrate
- `redis.asyncio` client — zero code changes needed for Dragonfly

## The Ask

Access to Dragonfly Cloud credits beyond the $100 trial, or a startup/design partner tier. Happy to get on a call to discuss.

Best,
Jade
Founder, JadeCLI
