To: startups@aiven.io
Subject: Startup Application — JadeCLI: Multi-Agent Context Bus on Aiven Dragonfly

Hi Aiven Team,

I'm Jade, founder of JadeCLI. We're building an open-source multi-agent orchestration system where Claude Code agents collaborate across distributed WSL2 runtimes.

## What We Built

We use a Redis-compatible store as a **Context Bus** between parallel AI agents. The pattern:

1. Agent A runs an expensive tool (web search, file grep, code analysis)
2. Result gets cached with a deterministic key (`tc:{tool}:{sha256}`)
3. Results over 512KB are stored by reference (`ctx:task:<uuid>`) — only a lightweight pointer passes through the LLM context window
4. Agent B hits cache instead of re-running the same tool — saving both compute and tokens

This cuts our token costs by ~40% on multi-agent runs and eliminates redundant API calls across the swarm.

## Why Dragonfly on Aiven

Our agents run write-heavy concurrent workloads (5-8 parallel agents writing cache entries simultaneously). Dragonfly's multi-threaded architecture handles this without the single-threaded bottleneck we'd hit on standard Redis. Aiven's managed service means we don't burn engineering time on ops.

## Tech Stack

- **Agents**: Claude Code (Anthropic) with custom hooks and tool caching
- **Orchestration**: Claude Agent SDK with team-based task delegation
- **Working Memory (Tier 2)**: Dragonfly — cache + inter-agent context bus
- **Persistent Memory (Tier 3)**: Neon Postgres (pgvector for embeddings)
- **Tracing**: MLflow 3.9
- **Dashboard**: Next.js on Vercel

## The Ask

We're currently on local Redis 8 and ready to move to managed Dragonfly. We'd love access to the Aiven startup program or extended trial credits to validate our architecture at scale before committing to a paid tier.

We're happy to publish our caching patterns as a case study showing Dragonfly as an AI agent memory layer — this is a novel use case that could drive adoption.

## Links

- GitHub: github.com/jadecli-ai
- Architecture: Multi-agent cache-first workflow with reference-passing
- 98 tests passing, 27 specifically for the cache layer

Best,
Jade
Founder, JadeCLI
