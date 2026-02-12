To: startups@redis.io (via https://redis.io/startups/)
Subject: Startup Program Application — JadeCLI Multi-Agent Cache Layer

Hi Redis Team,

I'm Jade, founder of JadeCLI. We're building an open-source multi-agent AI orchestration platform, and Redis is our working memory layer.

## How We Use Redis

Our system runs parallel Claude Code agents that share a Redis-backed context bus:

- **Tool result caching**: Deterministic keys (`tc:{tool}:{hash}`) prevent redundant expensive operations across agents
- **Reference-passing for large results**: Outputs over 512KB stored as `ctx:task:<uuid>` — agents exchange pointers instead of raw data, cutting token costs ~40%
- **Hook-driven auto-population**: Cache fills on PostToolUse events, zero manual intervention
- **Composable hook chains**: Multiple cache + logging + tracing hooks merged with error isolation

We're currently on Redis 8 and our entire async cache layer uses `redis.asyncio` (redis-py >= 5.0).

## Why Redis Cloud

We need a managed Redis instance that our distributed agent runtimes can share. Our agents run across multiple WSL2 distros and need a central memory store accessible over TLS. Redis Cloud gives us that without ops overhead.

## Tech Stack

- Claude Code + Claude Agent SDK (Anthropic)
- Redis 8 (migrating to Redis Cloud)
- Neon Postgres + pgvector (long-term storage)
- MLflow 3.9 (tracing)
- Next.js dashboard on Vercel

## The Ask

Access to the Redis Startup Program for credits and mentoring as we scale from local Redis to Redis Cloud. We're happy to share our caching architecture as a case study for Redis in the AI agent ecosystem.

## Metrics

- 98 tests (27 cache-specific)
- 5-8 concurrent agents per run
- Cache hit rates of 60-70% on multi-agent tasks

Best,
Jade
Founder, JadeCLI
