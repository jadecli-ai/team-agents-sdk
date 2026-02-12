# Anthropic GitHub Organization: Engineering Patterns

Research date: 2026-02-11

## Organization Structure (67 repos)

| Category | Naming | Count | Examples |
|----------|--------|-------|---------|
| API SDKs | `anthropic-sdk-{lang}` | 7 | python, typescript, go, java, ruby, csharp, php |
| Agent SDKs | `claude-agent-sdk-{lang}` | 2 | python, typescript |
| Claude tools | `claude-code-*` | 5 | claude-code, claude-code-action, claude-code-security-review |
| Skills/Plugins | descriptive names | 3 | skills, claude-plugins-official, knowledge-work-plugins |
| Research | paper-related names | ~20 | sleeper-agents-paper, attribution-graphs-frontend |
| Forks | original names | ~30 | httpcore, orjson, redis-py, triton |

## Key Pattern: Stainless Code Generation

All SDKs are auto-generated from a **single OpenAPI spec** using [Stainless](https://www.stainless.com/).

- `.stats.yml` in every repo tracks the OpenAPI spec hash
- Python and TS SDKs share the **same spec hash** — confirmed same source
- Generated files: `resources/`, `types/`, `_client`, error classes
- Safe zones (never overwritten): `lib/`, `examples/`, `helpers/`

## Repo Structure Pattern (consistent across all SDKs)

```
.github/workflows/
  ci.yml                     # Lint + Build + Test
  claude.yml                 # Claude Code review
  create-releases.yml        # release-please
  detect-breaking-changes.yml
  publish-{registry}.yml     # PyPI/npm/etc
  release-doctor.yml         # Release health checks

scripts/
  bootstrap                  # First-time setup
  lint                       # Code quality
  test                       # Test runner (starts Prism mock server)
  format                     # Auto-format
  build                      # Build artifacts

.release-please-manifest.json
release-please-config.json
CONTRIBUTING.md
CHANGELOG.md
```

## Cloud Adapter Pattern

Each SDK supports Bedrock/Vertex/Foundry adapters that:
- Extend the base client class
- Override authentication (AWS SigV4, Google OAuth)
- Override URL routing (cloud-specific endpoints)
- Re-expose the same resource hierarchy

| Language | Adapter Location |
|----------|-----------------|
| Python | `src/anthropic/lib/bedrock/`, `lib/vertex/` (inline, optional extras) |
| TypeScript | `packages/bedrock-sdk/`, `packages/vertex-sdk/` (separate npm packages) |
| Go | `bedrock/`, `vertex/` (sub-packages in same module) |
| Java | `anthropic-java-bedrock/` (separate Gradle module) |
| C# | `src/Anthropic.Bedrock/` (separate .NET project) |

## Build Tooling

| Language | Package Manager | Build System | Type Checker | Linter |
|----------|----------------|-------------|--------------|--------|
| Python | uv | hatchling | pyright + mypy | ruff |
| TypeScript | yarn v1 | tsc-multi (CJS+ESM) | tsc | eslint |
| Go | go modules | go build | go vet | - |
| Java | Gradle | Kotlin DSL | - | - |
| Ruby | Bundler | Rake | Sorbet + RBI | rubocop |
| C# | NuGet | .NET SDK | Roslyn | csharpier |
| PHP | Composer | - | PHPStan | php-cs-fixer |

## Agent SDK (separate from API SDK)

`claude-agent-sdk-python` (v0.1.35):
- Depends on `anyio>=4.0.0`, `mcp>=0.1.0` — NOT on `anthropic` SDK
- Structure: `src/claude_agent_sdk/{client.py, query.py, types.py, _internal/}`
- Wraps Claude Code CLI as a subprocess
- CLAUDE.md with lint/test/typecheck commands
- Uses hatchling build, ruff linting, mypy strict mode

## Release Pipeline

```
OpenAPI spec change
  → Stainless generates code
  → Push to generated branch
  → release-please creates Release PR (CHANGELOG.md + version bump)
  → Merge triggers publish workflow
  → Publish to PyPI/npm/etc
```

Sources:
- https://github.com/anthropics
- https://github.com/anthropics/anthropic-sdk-python
- https://github.com/anthropics/anthropic-sdk-typescript
- https://github.com/anthropics/claude-agent-sdk-python
- https://www.stainless.com/
