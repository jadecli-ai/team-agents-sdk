# Web Crawler Architecture for Claude Code -- Research Report (February 2026)

## 1. The llms.txt Standard

### What It Is

The `/llms.txt` file is a proposed standard by Jeremy Howard (Answer.AI). It tells LLMs how to consume a website's content at inference time. Over **844,000 websites** have implemented it.

### Specification

```markdown
# Project Name
> Short summary blockquote with key context

Optional free-form markdown paragraphs.

## Section Name
- [Link Title](https://url): Description of this resource

## Optional
- [Secondary Resource](https://url): Can be skipped for shorter context
```

### Companion Files

| File | Purpose |
|------|---------|
| `/llms.txt` | Navigation/structure index (~thousands of tokens) |
| `/llms-full.txt` | Complete documentation concatenated (can be 100K+ tokens) |

### Real-World Examples

| Company | llms.txt | llms-full.txt | URL |
|---------|----------|--------------|-----|
| Anthropic | ~8,364 tokens | ~481,349 tokens | `docs.claude.com/llms.txt` |
| Cloudflare | Structured by product | Full docs per service | `developers.cloudflare.com/llms.txt` |
| Stripe | By product categories | Uses `## Optional` | `stripe.com/llms.txt` |

---

## 2. MCP Servers for Web Crawling

### Tier 1: Already in Stack

**`@modelcontextprotocol/server-fetch`** -- Single-page fetch, HTML to markdown. No caching, no crawling.

**`redis-mcp-server`** -- Cache layer with TTL, hash ops, list ops.

### Tier 2: Recommended Additions

#### mcp-crawl4ai (Free, Recommended)

```bash
claude mcp add crawl4ai --scope user -- npx -y mcp-crawl4ai
```

**Tools**: `crawl_url`, `batch_crawl`, `deep_crawl` (recursive BFS/DFS), `extract_structured_data`, `extract_with_llm`, `crawl_with_js_execution`

**Key advantage**: Completely free, no API key, 58K+ GitHub stars, built-in caching.

#### Firecrawl MCP (API Key Required)

```json
"firecrawl": {
  "command": "npx",
  "args": ["-y", "firecrawl-mcp"],
  "env": { "FIRECRAWL_API_KEY": "YOUR_KEY" }
}
```

**Tools (8)**: `firecrawl_scrape`, `firecrawl_batch_scrape`, `firecrawl_crawl`, `firecrawl_map`, `firecrawl_search`, `firecrawl_extract`, status checkers.

**Key advantage**: Site mapping, natural language crawl config, async full-site crawl.

#### Jina AI Remote MCP (Zero Infrastructure)

```bash
claude mcp add -s user --transport http jina https://mcp.jina.ai/v1 \
  --header "Authorization: Bearer ${JINA_API_KEY}"
```

**Tools (19)**: `read_url`, `parallel_read_url`, `search_web`, `capture_screenshot_url`, etc.

**Key advantage**: Zero infrastructure, best markdown quality (ReaderLM-v2).

### Tier 3: Browser Automation (JS-Heavy Sites)

- **Playwright MCP**: `npx -y @playwright/mcp`
- **Browserbase MCP**: Cloud headless Chrome, anti-bot

---

## 3. Caching Strategies

### Strategy A: Redis Cache (Existing)

```
Key:   crawl:md:{domain}:{path_hash}
Value: JSON { url, title, markdown, fetched_at, ttl }
TTL:   86400 (24h dynamic), 604800 (7d docs)
```

### Strategy B: Filesystem Markdown Cache

```
~/.claude/crawl-cache/
  example.com/
    docs/api-reference.md
    llms.txt
    _meta.json
```

### Recommended Hybrid

1. **Redis** for hot cache (24h-7d TTL)
2. **Filesystem** for cold storage (permanent, git-trackable)
3. Check Redis -> filesystem -> fetch fresh

---

## 4. Proposed Crawler Agent Definition

Save as `~/.claude/agents/web-crawler.md`:

```yaml
---
name: web-crawler
description: Crawls websites systematically, discovers llms.txt files, converts pages to markdown, and caches results. Use when you need to fetch, index, or cache web documentation.
model: sonnet
memory: user
permissionMode: acceptEdits
maxTurns: 100
tools:
  - Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
  - mcp__fetch__fetch
  - mcp__redis__set, mcp__redis__get, mcp__redis__hset, mcp__redis__hget
  - mcp__filesystem__write_file, mcp__filesystem__read_text_file
  - mcp__memory__create_entities, mcp__memory__create_relations
---

You are a systematic web crawler agent.

## Workflow
1. Check for /llms.txt and /llms-full.txt first
2. Parse llms.txt for all linked URLs
3. Check Redis cache before fetching
4. Fetch & convert to markdown
5. Cache in Redis (7d docs, 24h dynamic)
6. Cache to filesystem (~/.claude/crawl-cache/{domain}/)
7. Index in knowledge graph

## Safety
- Respect robots.txt
- Max 50 pages per invocation
- 1 second between fetches
- Never crawl outside requested domain
```

---

## 5. Recommended Architecture

### Minimal (Zero New Infrastructure)

```
[Claude Code] --> [web-crawler subagent]
                      |--> mcp__fetch__fetch (single page)
                      |--> mcp__redis__* (cache with TTL)
                      |--> mcp__filesystem__* (persistent .md)
                      |--> mcp__memory__* (site structure graph)
```

### Recommended (One New MCP)

Add `mcp-crawl4ai` for recursive crawling:

```
[Claude Code] --> [web-crawler subagent]
                      |--> crawl4ai: deep_crawl (recursive)
                      |--> crawl4ai: batch_crawl (parallel)
                      |--> mcp__fetch__fetch (fallback)
                      |--> mcp__redis__* (hot cache)
                      |--> mcp__filesystem__* (cold cache)
```

### Cache Flow

```
Request URL
  --> Redis check (crawl:md:{domain}:{path_hash})
      --> HIT: return cached
      --> MISS: Filesystem check
          --> HIT: reload to Redis, return
          --> MISS: Fetch fresh -> cache both -> return
```

---

## 6. Package Summary

| Component | Package | Purpose |
|-----------|---------|---------|
| Fetch MCP | `@modelcontextprotocol/server-fetch` | Single-page fetch |
| Redis MCP | `redis-mcp-server` | Cache with TTL |
| Crawl4AI MCP | `npx -y mcp-crawl4ai` | Free recursive crawling |
| Firecrawl MCP | `npx -y firecrawl-mcp` | Site map/crawl (API key) |
| Jina MCP | `https://mcp.jina.ai/v1` | Best markdown, remote |
| Playwright MCP | `npx -y @playwright/mcp` | JS-heavy sites |

---

## Sources

- [llmstxt.org](https://llmstxt.org/)
- [Answer.AI llms.txt proposal](https://www.answer.ai/posts/2024-09-03-llmstxt.html)
- [Firecrawl MCP docs](https://docs.firecrawl.dev/mcp-server)
- [Crawl4AI MCP](https://github.com/vivmagarwal/mcp-crawl4ai)
- [Jina AI MCP](https://github.com/jina-ai/MCP)
- [Claude Code subagents docs](https://code.claude.com/docs/en/sub-agents)
- [MCP servers registry](https://mcpservers.org/)
