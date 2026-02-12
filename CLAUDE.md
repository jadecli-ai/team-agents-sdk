# jadecli-team-agents-sdk

Opus 4.6 team agent system using Claude Agent SDK + MLflow 3.9 GenAI tracing.

## Stack

| Package | Version | Purpose |
|---------|---------|---------|
| `claude-agent-sdk` | 0.1.33 | Python SDK wrapping Claude Code CLI |
| `mlflow[genai]` | 3.9.0 | Tracing + evaluation + UI |
| `mlflow-tracing` | latest | Lightweight prod-only tracing |

## Architecture

```
claude-agent-sdk  -->  wraps Claude Code CLI  -->  agents defined in .md files
         |
mlflow.anthropic.autolog()  -->  auto-traces all SDK calls (1 line)
         |
mlflow.genai.evaluate()  -->  built-in scorers for quality/performance
         |
MLflow 3.9 UI  -->  dashboards, judge builder, trace comparison
```

## Directory Structure

```
.claude/
  agents/       -- Agent definitions (.md with YAML frontmatter)
  tasks/        -- Task tracking files
research/       -- Research reports from initial investigation
scripts/        -- Automation and utility scripts
```

## Key Principles

1. **Minimize custom code** -- reuse SDK objects (ClaudeAgentOptions, AgentDefinition, HookMatcher)
2. **Agents as markdown** -- define agents in `.md` files, not Python classes
3. **One-line tracing** -- `mlflow.anthropic.autolog()` captures everything
4. **Built-in evaluation** -- `mlflow.genai.evaluate()` with scorers, not custom eval code
5. **Crawl with MCP** -- use mcp-crawl4ai + Redis cache, not custom scrapers

## Running

```bash
# Start MLflow tracking server
mlflow server --port 5000

# Run an agent query with tracing
python -c "
import mlflow, asyncio
from claude_agent_sdk import query, ClaudeAgentOptions
mlflow.anthropic.autolog()
mlflow.set_tracking_uri('http://localhost:5000')
asyncio.run(...)
"
```
