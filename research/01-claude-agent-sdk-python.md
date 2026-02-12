# Anthropic Claude Agent SDK for Python -- Research Report (February 2026)

## 1. Package Name and Installation

**PyPI package**: `claude-agent-sdk`
**Repository**: [github.com/anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)

The package was renamed from the original `claude-code-sdk` (now deprecated) to `claude-agent-sdk` to reflect its broader scope beyond just coding tasks.

```bash
# pip
pip install claude-agent-sdk

# uv (recommended)
uv init && uv add claude-agent-sdk

# From virtual environment
python3 -m venv .venv && source .venv/bin/activate
pip3 install claude-agent-sdk
```

**Requirements**: Python 3.10+ (supports 3.10, 3.11, 3.12, 3.13). The Claude Code CLI is **automatically bundled** with the package -- no separate install needed. License: MIT. Latest release as of Feb 7, 2026. Development status: Alpha.

**Authentication**: Set `ANTHROPIC_API_KEY` environment variable, or use Bedrock (`CLAUDE_CODE_USE_BEDROCK=1`), Vertex AI (`CLAUDE_CODE_USE_VERTEX=1`), or Azure AI Foundry (`CLAUDE_CODE_USE_FOUNDRY=1`).

---

## 2. Core Classes and Objects

### Primary Import Path

```python
from claude_agent_sdk import (
    # Functions
    query,
    tool,
    create_sdk_mcp_server,
    # Classes
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AgentDefinition,
    HookMatcher,
    HookContext,
    # Message types
    Message,
    UserMessage,
    AssistantMessage,
    SystemMessage,
    ResultMessage,
    StreamEvent,
    # Content blocks
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    ToolResultBlock,
    # Errors
    ClaudeSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
    CLIJSONDecodeError,
    # Permission types
    PermissionResultAllow,
    PermissionResultDeny,
)
```

### Two Primary Entry Points

The SDK provides two ways to interact with Claude:

| Feature | `query()` | `ClaudeSDKClient` |
|---------|-----------|-------------------|
| Session | Creates new session each time | Reuses same session |
| Conversation | Single exchange | Multiple exchanges in same context |
| Interrupts | Not supported | Supported |
| Hooks | Not supported | Supported |
| Custom Tools | Not supported | Supported |
| Continue Chat | New session each time | Maintains conversation |

#### `query()` -- Simple One-Shot Function

```python
async def query(
    *,
    prompt: str | AsyncIterable[dict[str, Any]],
    options: ClaudeAgentOptions | None = None
) -> AsyncIterator[Message]
```

Minimal example:

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Find and fix the bug in auth.py",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"]),
    ):
        print(message)

asyncio.run(main())
```

#### `ClaudeSDKClient` -- Stateful Client

```python
class ClaudeSDKClient:
    def __init__(self, options: ClaudeAgentOptions | None = None)
    async def connect(self, prompt: str | AsyncIterable[dict] | None = None) -> None
    async def query(self, prompt: str | AsyncIterable[dict], session_id: str = "default") -> None
    async def receive_messages(self) -> AsyncIterator[Message]
    async def receive_response(self) -> AsyncIterator[Message]
    async def interrupt(self) -> None
    async def rewind_files(self, user_message_uuid: str) -> None
    async def disconnect(self) -> None
```

Used as an async context manager:

```python
async with ClaudeSDKClient(options=options) as client:
    await client.query("What's the capital of France?")
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

    # Follow-up with full context retained
    await client.query("What's the population of that city?")
    async for message in client.receive_response():
        ...
```

### `ClaudeAgentOptions` -- Full Configuration Dataclass

Key fields (partial list -- see full reference for all 30+ fields):

```python
@dataclass
class ClaudeAgentOptions:
    tools: list[str] | ToolsPreset | None = None
    allowed_tools: list[str] = field(default_factory=list)
    system_prompt: str | SystemPromptPreset | None = None
    mcp_servers: dict[str, McpServerConfig] | str | Path = field(default_factory=dict)
    permission_mode: PermissionMode | None = None     # "default"|"acceptEdits"|"plan"|"bypassPermissions"
    max_turns: int | None = None
    max_budget_usd: float | None = None
    model: str | None = None
    cwd: str | Path | None = None
    agents: dict[str, AgentDefinition] | None = None   # Subagent definitions
    hooks: dict[HookEvent, list[HookMatcher]] | None = None
    can_use_tool: CanUseTool | None = None              # Permission callback
    resume: str | None = None                           # Session ID to resume
    setting_sources: list[SettingSource] | None = None  # "user"|"project"|"local"
    sandbox: SandboxSettings | None = None
    include_partial_messages: bool = False
    max_thinking_tokens: int | None = None
    output_format: OutputFormat | None = None           # JSON schema validation
    plugins: list[SdkPluginConfig] = field(default_factory=list)
```

### `AgentDefinition` -- Subagent Configuration

```python
@dataclass
class AgentDefinition:
    description: str          # When to use this agent
    prompt: str               # The agent's system prompt
    tools: list[str] | None = None    # Allowed tools (inherits all if omitted)
    model: Literal["sonnet", "opus", "haiku", "inherit"] | None = None
```

---

## 3. Multi-Agent Teams (Orchestrator, Handoff, Subagent Patterns)

### Programmatic Subagents via the SDK

The primary multi-agent pattern is the **orchestrator-subagent** model. You define subagents in `ClaudeAgentOptions.agents` and include `"Task"` in `allowed_tools`. The main agent spawns subagents via the `Task` tool.

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

async for message in query(
    prompt="Use the code-reviewer agent to review this codebase, "
           "then use the test-runner to verify changes",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep", "Task"],
        agents={
            "code-reviewer": AgentDefinition(
                description="Expert code reviewer for quality and security reviews.",
                prompt="Analyze code quality and suggest improvements.",
                tools=["Read", "Glob", "Grep"],
            ),
            "test-runner": AgentDefinition(
                description="Runs tests and reports results.",
                prompt="Execute test suites and report failures.",
                tools=["Bash", "Read", "Glob"],
                model="haiku",  # Use cheaper model for test running
            ),
        },
    ),
):
    if hasattr(message, "result"):
        print(message.result)
```

### File-Based Subagents (Markdown with YAML Frontmatter)

Subagents can also be defined as `.md` files:

- **Project-level**: `.claude/agents/code-reviewer.md`
- **User-level**: `~/.claude/agents/code-reviewer.md`
- **CLI flag**: `claude --agents '{...}'` (JSON)

Example file at `.claude/agents/code-reviewer.md`:

```markdown
---
name: code-reviewer
description: Expert code review specialist. Use immediately after code changes.
tools: Read, Grep, Glob, Bash
model: sonnet
memory: user
---

You are a senior code reviewer. Focus on quality, security, and best practices.
```

### Key Multi-Agent Patterns

1. **Orchestrator-Worker**: Main agent delegates to specialized subagents, each with their own context window. Subagents return summaries to the orchestrator.

2. **Parallel Research**: Spawn multiple subagents simultaneously for independent investigations.

3. **Chained Subagents**: Sequential delegation where output of one subagent feeds into the next.

4. **Background Subagents**: Run concurrently while the main conversation continues.

5. **Foreground Subagents**: Block the main conversation until complete; permission prompts pass through to the user.

### Built-in Subagents

Claude Code includes several built-in subagents:
- **Explore**: Haiku-based, read-only, for codebase search/analysis
- **Plan**: Research agent for plan mode, inherits parent model
- **General-purpose**: Full tool access for complex multi-step tasks
- **Bash**: Terminal commands in separate context

### Constraints

- Subagents **cannot spawn other subagents** (no nesting).
- Messages from subagents include a `parent_tool_use_id` field for tracking.
- Subagents can be **resumed** with their full conversation history.
- Persistent memory across sessions is available via the `memory` field (`user`, `project`, or `local` scope).

---

## 4. Built-in Tools

| Tool | Description |
|------|-------------|
| **Read** | Read any file in the working directory |
| **Write** | Create new files |
| **Edit** | Make precise edits to existing files |
| **Bash** | Run terminal commands, scripts, git operations |
| **Glob** | Find files by pattern |
| **Grep** | Search file contents with regex |
| **WebSearch** | Search the web for current information |
| **WebFetch** | Fetch and parse web page content |
| **NotebookEdit** | Edit Jupyter notebook cells |
| **Task** | Spawn subagents for delegation |
| **AskUserQuestion** | Ask the user clarifying questions with multiple choice |
| **TodoWrite** | Manage task lists |
| **BashOutput** | Read output from background shell processes |
| **KillBash** | Kill background shell processes |
| **ExitPlanMode** | Exit plan mode with a proposed plan |

### Custom Tools (In-Process MCP Servers)

The `@tool` decorator creates custom tools that run in-process (no subprocess overhead):

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

@tool("greet", "Greet a user", {"name": str})
async def greet(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}

@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args):
    return {"content": [{"type": "text", "text": f"Sum: {args['a'] + args['b']}"}]}

server = create_sdk_mcp_server(name="my-tools", version="1.0.0", tools=[greet, add])

options = ClaudeAgentOptions(
    mcp_servers={"tools": server},
    allowed_tools=["mcp__tools__greet", "mcp__tools__add"],
)
```

MCP tool naming convention: `mcp__<server-name>__<tool-name>`

---

## 5. Agent Communication and Delegation

Agents communicate through the **Task tool**. When the main agent decides to delegate, it invokes `Task` with:

```python
{
    "description": str,       # Short 3-5 word description
    "prompt": str,            # The task for the subagent
    "subagent_type": str,     # Name of the specialized agent to use
}
```

The Task tool returns:

```python
{
    "result": str,             # Final result from the subagent
    "usage": dict | None,      # Token usage statistics
    "total_cost_usd": float | None,
    "duration_ms": int | None,
}
```

### Session Continuity

Sessions can be resumed to maintain context across multiple exchanges:

```python
session_id = None

# First query: capture session ID
async for message in query(
    prompt="Read the authentication module",
    options=ClaudeAgentOptions(allowed_tools=["Read", "Glob"]),
):
    if hasattr(message, "subtype") and message.subtype == "init":
        session_id = message.session_id

# Resume with full context
async for message in query(
    prompt="Now find all places that call it",
    options=ClaudeAgentOptions(resume=session_id),
):
    if hasattr(message, "result"):
        print(message.result)
```

---

## 6. Integration with Claude Code CLI

The Claude Agent SDK **wraps the Claude Code CLI** as its runtime engine:

- The SDK bundles the Claude Code CLI automatically.
- Custom CLI path: `ClaudeAgentOptions(cli_path="/path/to/claude")`.
- Communication via JSON over stdin/stdout.

**SDK vs CLI comparison:**

| Use case | Best choice |
|----------|-------------|
| Interactive development | CLI |
| CI/CD pipelines | SDK |
| Custom applications | SDK |
| One-off tasks | CLI |
| Production automation | SDK |

---

## 7. Relationship Between `anthropic-sdk-python` and `claude-agent-sdk-python`

| Aspect | `anthropic` (Client SDK) | `claude-agent-sdk` (Agent SDK) |
|--------|--------------------------|-------------------------------|
| **PyPI package** | `anthropic` | `claude-agent-sdk` |
| **Abstraction** | Low-level Messages API | High-level autonomous agents |
| **Tool execution** | You implement the tool loop | Claude handles tools autonomously |
| **Built-in tools** | None | Read, Write, Edit, Bash, Glob, Grep, etc. |
| **Session management** | None | Built-in session persistence and resumption |
| **Subagents** | None | Built-in orchestrator-subagent pattern |

The Agent SDK does **not** depend on `anthropic-sdk-python`. It wraps the Claude Code CLI binary.

---

## 8. Tracing and Observability

### Built-in Hooks System

| Hook Event | Description |
|-----------|-------------|
| `PreToolUse` | Before tool execution (can block/modify) |
| `PostToolUse` | After tool execution (can log/audit) |
| `UserPromptSubmit` | When user submits a prompt |
| `Stop` | When agent execution stops |
| `SubagentStop` | When a subagent completes |
| `PreCompact` | Before conversation compaction |

### `ResultMessage` Cost/Usage Tracking

```python
@dataclass
class ResultMessage:
    subtype: str
    duration_ms: int
    duration_api_ms: int
    is_error: bool
    num_turns: int
    session_id: str
    total_cost_usd: float | None = None
    usage: dict[str, Any] | None = None
    result: str | None = None
```

### Third-Party Observability Integrations

1. **MLflow**: `mlflow.anthropic.autolog()` for automatic tracing
2. **Langfuse** (OpenTelemetry-based): Full tool call and model I/O tracing
3. **LangSmith/LangChain**: Execution trace integration
4. **OpenTelemetry / claude_telemetry**: Drop-in wrapper for metrics export

---

## Sources

- [Agent SDK Overview](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Agent SDK Python Reference](https://platform.claude.com/docs/en/agent-sdk/python)
- [Agent SDK Quickstart](https://platform.claude.com/docs/en/agent-sdk/quickstart)
- [GitHub: anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)
- [claude-agent-sdk on PyPI](https://pypi.org/project/claude-agent-sdk/)
- [Agent SDK Hooks Documentation](https://platform.claude.com/docs/en/agent-sdk/hooks)
- [Create Custom Subagents](https://code.claude.com/docs/en/sub-agents)
- [Building Agents with the Claude Agent SDK](https://claude.com/blog/building-agents-with-the-claude-agent-sdk)
- [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)
