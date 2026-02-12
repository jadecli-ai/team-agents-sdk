To: Via https://startupcredits.io/s/upstash
Subject: Startup Credits Application — JadeCLI Serverless Agent Memory

Hi Upstash Team,

I'm Jade, building JadeCLI — an open-source multi-agent AI system. We're interested in Upstash Redis as our serverless working memory layer.

## Why Upstash

Our agents run in bursts — a multi-agent task spins up 5-8 agents for 10-30 minutes, generates hundreds of cache operations, then goes idle. Pay-per-command pricing is a perfect fit for this bursty workload pattern. We don't need a server running 24/7 for what amounts to 2-3 hours of active use per day.

## The Architecture

- **Cache keys**: `tc:{tool_name}:{sha256(input)[:16]}` — deterministic, deduplicates across agents
- **Reference-passing**: Large results (>512KB) stored as `ctx:task:<uuid>`, agents pass pointers
- **TTL-managed**: 300s for file ops, 900s for web ops, 3600s for context refs
- **Async client**: `redis.asyncio` with TLS — compatible with Upstash's `rediss://` endpoint

## Usage Pattern

- ~500-2000 commands per multi-agent run
- 3-5 runs per day during active development
- Peaks at ~50 concurrent connections during parallel agent execution
- Total: well within free tier initially, scaling to pay-as-you-go

## Tech Stack

- Claude Code agents (Anthropic)
- Neon Postgres (persistent storage)
- MLflow 3.9 (tracing)
- Next.js on Vercel (dashboard)

## The Ask

Startup credits to support our growth past the free tier as we scale agent concurrency.

Best,
Jade
Founder, JadeCLI
