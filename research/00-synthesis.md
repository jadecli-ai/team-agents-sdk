# Team Agents Stack -- Research Synthesis (Feb 2026)

## The Minimal-Code Stack

```
claude-agent-sdk (pip)  -->  wraps Claude Code CLI  -->  agents in .md files
         |
mlflow.anthropic.autolog()  -->  auto-traces all calls (1 line)
         |
mlflow.genai.evaluate()  -->  built-in scorers (3 lines)
         |
MLflow 3.9 UI  -->  dashboards, judge builder, trace comparison
```

## Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `claude-agent-sdk` | 0.1.33 | Python SDK wrapping Claude Code CLI |
| `mlflow[genai]` | 3.9.0 | Tracing + evaluation + UI |
| `mlflow-tracing` | latest | Lightweight prod-only tracing (95% smaller) |

## Key SDK Objects (Reuse, Don't Rewrite)

- `ClaudeAgentOptions` -- 30+ config fields
- `AgentDefinition` -- subagent config (description, prompt, tools, model)
- `ClaudeSDKClient` -- stateful multi-turn async client
- `query()` -- one-shot async function
- `@tool` + `create_sdk_mcp_server()` -- custom in-process MCP tools
- `HookMatcher` -- observability callbacks (PreToolUse, PostToolUse)
- `ResultMessage` -- has total_cost_usd, duration_ms, num_turns
- `mlflow.anthropic.autolog()` -- auto-traces everything
- `mlflow.genai.evaluate()` -- runs scorers on traces
- `mlflow.search_traces()` -- programmatic trace queries
- `SpanType` enum -- AGENT, TOOL, LLM, TASK, GUARDRAIL, etc.

## Agent Definition Format (.md files)

Frontmatter fields: name, description, tools, disallowedTools, model,
permissionMode, maxTurns, memory, mcpServers, skills, hooks

Place in: `~/.claude/agents/` (user) or `.claude/agents/` (project)

## MLflow 3.9 Key Features

- `mlflow.anthropic.autolog()` -- auto-traces Claude Agent SDK
- `mlflow autolog claude` -- CLI tracing for interactive sessions
- Trace Overview Dashboard -- pre-built performance/quality metrics
- Judge Builder UI -- create custom LLM judges without code
- Online Monitoring -- auto-run judges on traces
- MemAlignOptimizer -- judges improve from feedback over time
- Distributed tracing -- cross-service trace propagation
- AI Gateway built into tracking server

## Crawling Architecture

### MCP Servers (by tier)
- Tier 1 (already have): fetch, redis
- Tier 2 (recommended): mcp-crawl4ai (free, recursive, cached)
- Tier 2 (optional): firecrawl-mcp (requires API key, site mapping)
- Tier 2 (optional): jina MCP (remote, best markdown quality)
- Tier 3 (JS-heavy): playwright MCP, browserbase MCP

### llms.txt Standard
- `/llms.txt` -- navigation index in markdown
- `/llms-full.txt` -- complete docs concatenated
- 844K+ sites adopted; Anthropic, Cloudflare, Stripe use it

### Cache Strategy
- Redis: hot cache (24h-7d TTL), URL-keyed
- Filesystem: cold cache (~/.claude/crawl-cache/{domain}/)
- Check Redis -> filesystem -> fetch fresh

## Agent Teams (Experimental)

Enable: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Team lead coordinates, teammates are independent sessions
- Shared task list + mailbox for inter-agent messaging
- Delegate mode: lead restricted to coordination only
- tmux split-pane or in-process display modes
