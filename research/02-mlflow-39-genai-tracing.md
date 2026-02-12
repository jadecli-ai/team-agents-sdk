# MLflow 3.9 GenAI Tracing -- Complete Reference (February 2026)

## 1. Installation

MLflow 3.9.0 was released on **January 29, 2026** and requires **Python 3.10+**.

```bash
# Core install
pip install mlflow>=3.9

# With GenAI extras (recommended for tracing)
pip install 'mlflow[genai]'

# Lightweight tracing-only package for production
pip install mlflow-tracing   # 95% smaller footprint than full mlflow
```

---

## 2. The GenAI Tracing System

MLflow Tracing is a fully **OpenTelemetry-compatible** observability solution.

### Core Architecture

**TraceInfo** (metadata layer):
| Field | Type | Purpose |
|-------|------|---------|
| `trace_id` | String | Primary identifier |
| `request_time` | Integer | Start time (milliseconds) |
| `state` | Enum | `OK`, `ERROR`, `IN_PROGRESS`, `UNSPECIFIED` |
| `execution_duration` | Integer | Total runtime (milliseconds) |
| `token_usage` | Dictionary | Aggregated token counts |
| `tags` | Dictionary | Mutable key-value pairs for filtering |

**TraceData**: Contains hierarchical **Span** objects forming a tree.

### Three Ways to Enable Tracing

1. **Auto-Tracing** -- `mlflow.<provider>.autolog()`
2. **Manual Instrumentation** -- `@mlflow.trace` decorator, `mlflow.start_span` context manager
3. **OpenTelemetry Export** -- direct OTLP trace export

---

## 3. Built-in Anthropic/Claude Integration

### Auto-Tracing (One Line)

```python
import anthropic
import mlflow

mlflow.anthropic.autolog()
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("Anthropic")

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=512,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
```

### What Gets Captured Automatically

- Prompts and completion responses
- Latencies per span
- Model name, temperature, max_tokens
- Function/tool calling instructions and results
- Token usage (`input_tokens`, `output_tokens`, `total_tokens`)
- Exceptions

### Claude Agent SDK Integration (MLflow >= 3.5)

```python
import asyncio
import mlflow.anthropic
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

mlflow.anthropic.autolog()
mlflow.set_experiment("my_claude_app")

options = ClaudeAgentOptions(
    allowed_tools=["mcp__travel__search_flights"],
    system_prompt="You are a travel assistant.",
    max_turns=10,
)

async def main():
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Find flights from NYC to London")
        async for message in client.receive_response():
            print(message)

asyncio.run(main())
```

### Claude Code CLI Tracing (MLflow >= 3.4)

```bash
mlflow autolog claude
mlflow autolog claude ~/my-project
mlflow autolog claude --status
mlflow autolog claude --disable
mlflow autolog claude -u http://localhost:5000 -n "My Project"
```

---

## 4. Key Classes and APIs

### SpanType Enum (`mlflow.entities.SpanType`)

```python
from mlflow.entities import SpanType

SpanType.AGENT        # Agent orchestration
SpanType.CHAIN        # Chain of operations
SpanType.CHAT_MODEL   # Chat model invocation
SpanType.EMBEDDING    # Embedding generation
SpanType.LLM          # LLM call
SpanType.MEMORY       # Memory retrieval
SpanType.PARSER       # Output parsing
SpanType.RERANKER     # Reranking step
SpanType.RETRIEVER    # Document retrieval
SpanType.TOOL         # Tool execution
SpanType.WORKFLOW     # Workflow orchestration
SpanType.TASK         # Task execution
SpanType.GUARDRAIL    # Safety guardrail
SpanType.EVALUATOR    # Evaluation step
SpanType.UNKNOWN      # Unspecified
```

### Tool-Calling Agent with Manual Span Annotations

```python
import anthropic
import mlflow
import asyncio
from mlflow.entities import SpanType

mlflow.anthropic.autolog()
client = anthropic.AsyncAnthropic()

@mlflow.trace(span_type=SpanType.TOOL)
async def get_weather(city: str) -> str:
    if city == "Tokyo": return "sunny"
    elif city == "Paris": return "rainy"
    return "unknown"

@mlflow.trace(span_type=SpanType.AGENT)
async def run_tool_agent(question: str):
    messages = [{"role": "user", "content": question}]
    ai_msg = await client.messages.create(
        model="claude-sonnet-4-5-20250929",
        messages=messages,
        tools=tools,
        max_tokens=2048,
    )
    # ... tool execution loop ...
    return response.content[-1].text
```

---

## 5. Viewing Traces in MLflow UI

### Start the MLflow Server

```bash
# Simple local server (SQLite backend, default since MLflow 3.7)
mlflow server --port 5000

# Docker Compose (PostgreSQL + MinIO)
cd mlflow/docker-compose && docker compose up -d
```

### MLflow 3.9 New UI Features

- **MLflow Assistant**: In-product chatbot powered by Claude Code
- **Trace Overview Dashboard**: Pre-built performance/quality metrics
- **Judge Builder UI**: Create custom LLM judges without code
- **Online Monitoring**: Auto-run judges on traces

---

## 6. Analyzing Traces Programmatically

```python
import mlflow

# Search with SQL-like DSL
traces_df = mlflow.search_traces(filter_string="trace.status = 'OK'")

# Complex queries
mlflow.search_traces(
    filter_string="""
        tag.environment = 'production'
        AND trace.status = 'ERROR'
        AND trace.execution_time_ms > 500
    """
)

# Token usage analysis
trace = mlflow.get_trace("<trace-id>")
print(trace.info.token_usage)
for span in trace.data.spans:
    if usage := span.get_attribute("mlflow.chat.tokenUsage"):
        print(f"{span.name}: {usage}")
```

---

## 7. GenAI Evaluation Features

```python
import mlflow
from mlflow.genai.scorers import Correctness, Guidelines
from mlflow.genai import scorer

eval_dataset = [
    {"inputs": {"question": "Capital of France?"}, "expectations": {"expected_response": "Paris"}},
]

@scorer
def is_concise(outputs: str) -> bool:
    return len(outputs.split()) <= 5

results = mlflow.evaluate(
    data=eval_dataset,
    predict_fn=qa_predict_fn,
    scorers=[
        Correctness(),
        Guidelines(name="is_english", guidelines="The answer must be in English"),
        is_concise,
    ],
)
```

### Using Different LLM Judges

```python
from mlflow.genai.scorers import Correctness
Correctness(model="anthropic:/claude-sonnet-4-20250514")
Correctness(model="bedrock:/anthropic.claude-sonnet-4-20250514")
```

### MLflow 3.9-Specific Features

- **MemAlignOptimizer**: Learns from historical feedback for more accurate judge evaluations
- **Judge Builder UI**: Define and iterate on custom LLM judge prompts in the UI
- **Online Monitoring with LLM Judges**: Auto-evaluate production traces
- **Metaprompting**: `mlflow.genai.optimize_prompts()`
- **Distributed tracing**: Cross-service trace propagation via `mlflow.tracing.distributed`
- **AI Gateway**: Built into the tracking server (no separate process)

---

## 8. MLflow Tracking Server Setup

| Method | Backend | Artifact Store | Notes |
|--------|---------|---------------|-------|
| `mlflow server` | SQLite (default) | Local filesystem | Simplest for dev |
| Docker Compose | PostgreSQL | MinIO (S3-compatible) | Production-ready |
| Kubernetes | PostgreSQL | S3/GCS/Azure Blob | Helm charts available |

---

## Summary

| Feature | Status |
|---------|--------|
| Anthropic autolog tracing | Stable (`mlflow.anthropic.autolog()`) |
| Claude Agent SDK tracing | Stable (>= MLflow 3.5) |
| Claude Code CLI tracing | Stable (>= MLflow 3.4) |
| Distributed tracing | New in 3.9 |
| AI Gateway in tracking server | New in 3.9 |
| MLflow Assistant (Claude-powered) | New in 3.9 |
| Trace Overview Dashboard | New in 3.9 |
| Online LLM Judge Monitoring | New in 3.9 |
| Judge Builder UI | New in 3.9 |
| MemAlign Judge Optimizer | New in 3.9 |
| 20+ framework integrations | Stable |
| OpenTelemetry compatibility | Stable |
| Lightweight `mlflow-tracing` package | Stable |

---

## Sources

- [MLflow Tracing for LLM Observability](https://mlflow.org/docs/latest/genai/tracing/)
- [Tracing Anthropic](https://mlflow.org/docs/latest/genai/tracing/integrations/listing/anthropic/)
- [mlflow.anthropic API Reference](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.anthropic.html)
- [Tracing Claude Code](https://mlflow.org/docs/latest/genai/tracing/integrations/listing/claude_code/)
- [MLflow autolog Claude Agents SDK](https://mlflow.org/blog/mlflow-autolog-claude-agents-sdk)
- [GenAI Evaluation Quickstart](https://mlflow.org/docs/latest/genai/eval-monitor/quickstart/)
- [MLflow 3.9.0 Release](https://github.com/mlflow/mlflow/releases/tag/v3.9.0)
