# Claude Code CLI Programmatic Usage -- Research Report (February 2026)

## 1. Claude Agent SDK -- The Official Programmatic Interface

The Claude Code SDK has been **renamed to the Claude Agent SDK**. It wraps the Claude Code CLI as a subprocess internally.

**Installation:**
```bash
pip install claude-agent-sdk          # Python
npm install @anthropic-ai/claude-agent-sdk  # TypeScript
```

**Latest PyPI version**: `0.1.33`

---

## 2. Three Ways to Invoke Claude Code from Python

### Method A: `query()` -- One-shot tasks

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are an expert Python developer",
        permission_mode="acceptEdits",
        allowed_tools=["Read", "Edit", "Bash"],
        cwd="/home/user/project",
    )
    async for message in query(prompt="Find and fix the bug in auth.py", options=options):
        print(message)

asyncio.run(main())
```

### Method B: `ClaudeSDKClient` -- Multi-turn conversations

```python
async with ClaudeSDKClient(options=options) as client:
    await client.query("What's in auth.py?")
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
    # Follow-up with full context
    await client.query("Now refactor the login function")
    async for message in client.receive_response():
        ...
```

### Method C: Subprocess via CLI

```python
import subprocess, json
result = subprocess.run(
    ["claude", "-p", "Summarize this project", "--output-format", "json"],
    capture_output=True, text=True, cwd="/path/to/project"
)
data = json.loads(result.stdout)
```

| Approach | Best for | Custom tools | Session persistence |
|----------|----------|--------------|---------------------|
| `query()` | One-shot automation | No | No |
| `ClaudeSDKClient` | Multi-turn, interactive apps | Yes | Yes |
| `subprocess` CLI | Simple scripts, CI/CD | No | Via `--resume` flag |

---

## 3. CLI Automation Flags

| Flag | Description |
|------|-------------|
| `-p, --print "prompt"` | Non-interactive mode |
| `--output-format json` | Structured JSON with metadata |
| `--output-format stream-json` | NDJSON for real-time streaming |
| `--json-schema '{...}'` | Enforce validated JSON output |
| `--max-turns 5` | Limit agentic turns |
| `--max-budget-usd 5.00` | Set spending cap |
| `--model sonnet` | Choose model |
| `--allowedTools "Bash,Read,Edit"` | Auto-approve specific tools |
| `--resume <session-id>` | Resume a previous session |
| `--agents '{...}'` | Define subagents via JSON |

### JSON output structure

```json
{
  "type": "result",
  "subtype": "success",
  "result": "This project is...",
  "session_id": "abc-123-def",
  "total_cost_usd": 0.042,
  "is_error": false,
  "duration_ms": 8500,
  "num_turns": 3
}
```

---

## 4. Custom Agents (File-Based)

### Agent Definition Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (lowercase, hyphens) |
| `description` | Yes | When to delegate |
| `tools` | No | Allowlist; inherits all if omitted |
| `disallowedTools` | No | Denylist |
| `model` | No | `sonnet`, `opus`, `haiku`, or `inherit` |
| `permissionMode` | No | `default`, `acceptEdits`, `plan`, `bypassPermissions`, `dontAsk`, `delegate` |
| `maxTurns` | No | Max agentic turns |
| `skills` | No | Skills to preload |
| `mcpServers` | No | MCP servers for this subagent |
| `hooks` | No | Lifecycle hooks |
| `memory` | No | Persistent memory: `user`, `project`, or `local` |

### Built-in Subagents

| Agent | Model | Purpose |
|-------|-------|---------|
| **Explore** | Haiku | Fast, read-only codebase search |
| **Plan** | Inherits | Research for plan mode |
| **General-purpose** | Inherits | Complex multi-step tasks |
| **Bash** | Inherits | Terminal commands |
| **Claude Code Guide** | Haiku | Questions about Claude Code features |

---

## 5. Permission Control

```python
async def custom_permission_handler(tool_name, input_data, context):
    if tool_name == "Write" and input_data.get("file_path", "").startswith("/system/"):
        return PermissionResultDeny(message="System writes blocked", interrupt=True)
    if tool_name == "Bash" and "rm -rf" in input_data.get("command", ""):
        return PermissionResultDeny(message="Dangerous command blocked")
    return PermissionResultAllow(updated_input=input_data)

options = ClaudeAgentOptions(can_use_tool=custom_permission_handler)
```

---

## 6. Agent Teams (Experimental)

Enable with: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

- Team lead coordinates, teammates are independent sessions
- Shared task list + mailbox for inter-agent messaging
- Modes: `in-process` (one terminal), `tmux` (split-pane)
- Delegate mode: lead restricted to coordination only

```
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
```

---

## 7. Session Management

```bash
# Resume most recent session
claude -p "Continue that review" --continue

# Resume specific session
session_id=$(claude -p "Start a review" --output-format json | jq -r '.session_id')
claude -p "Continue that review" --resume "$session_id"
```

### Python SDK session resume

```python
# Capture session ID from init message
async for message in query(prompt="Read auth module", options=options):
    if hasattr(message, "subtype") and message.subtype == "init":
        session_id = message.session_id

# Resume
async for message in query(
    prompt="Now find all callers",
    options=ClaudeAgentOptions(resume=session_id),
):
    ...
```

---

## Key Orchestration Patterns

1. **Cost control**: `--max-budget-usd` and `--max-turns`
2. **Model routing**: Haiku for exploration, Sonnet/Opus for implementation
3. **Permission isolation**: Each subagent has own tool restrictions
4. **Context preservation**: Subagents return summaries, not full output
5. **Structured output**: `--json-schema` for machine-parseable results

---

## Sources

- [Agent SDK Overview](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Python SDK Reference](https://platform.claude.com/docs/en/agent-sdk/python)
- [Run Claude Code Programmatically](https://code.claude.com/docs/en/headless)
- [CLI Reference](https://code.claude.com/docs/en/cli-reference)
- [Create Custom Subagents](https://code.claude.com/docs/en/sub-agents)
- [Agent Teams](https://code.claude.com/docs/en/agent-teams)
- [Session Management](https://platform.claude.com/docs/en/agent-sdk/sessions)
- [claude-agent-sdk on PyPI](https://pypi.org/project/claude-agent-sdk/)
