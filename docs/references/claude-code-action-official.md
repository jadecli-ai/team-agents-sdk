# Claude Code Action (Official)

> Source: https://github.com/anthropics/claude-code-action
> Fetched: 2026-02-11

## What It Does

GitHub Action that integrates Claude AI into your development workflow. It can answer questions and implement code changes on pull requests and issues. The action automatically detects context — whether responding to @claude mentions, issue assignments, or automation tasks — and intelligently selects execution modes without requiring configuration.

**Key capabilities:**
- Code review and analysis
- Implementation of fixes and features
- Interactive Q&A about codebases
- PR/issue integration with progress tracking
- Structured JSON outputs for automation

## Required Secrets

### Anthropic Direct API
- **`ANTHROPIC_API_KEY`** — Your Anthropic API key

### AWS Bedrock
- AWS credentials via OIDC (see cloud-providers.md)

### Google Vertex AI
- Google Cloud credentials via OIDC

### Microsoft Foundry (Azure)
- Azure credentials via OIDC

## Quickstart

```bash
claude /install-github-app
```

This command guides you through:
1. Creating/configuring a GitHub App
2. Installing it on your repository
3. Adding required secrets automatically

Requirements: Must be a repository admin. Only available for Anthropic API users.

## Workflow Examples

### PR Code Review

```yaml
name: PR Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: |
            Review this PR and provide constructive feedback on:
            - Code quality and best practices
            - Potential bugs or edge cases
            - Performance considerations
            - Security implications
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Issue-Based Implementation

```yaml
name: Claude Implementation
on:
  issues:
    types: [labeled]

jobs:
  implement:
    if: github.event.label.name == 'claude-implement'
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: |
            Implement the changes described in this issue.
            Create a pull request with your implementation.
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### @claude Mention Response

```yaml
name: Interactive Claude
on:
  issue_comment:
    types: [created]

jobs:
  respond:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: |
            Respond helpfully to the user's question about this codebase.
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Configuration

| Input | Description |
|-------|-------------|
| `prompt` | Custom instructions for Claude |
| `claude_args` | Additional Claude SDK arguments |
| `ANTHROPIC_API_KEY` | API key (or use cloud provider OIDC) |

### Permissions Required

```yaml
permissions:
  contents: read          # For code review
  contents: write         # For code implementation
  pull-requests: write    # To comment on PRs
  issues: write          # To comment on issues
```

## Stats
- Stars: 5.6k
- License: MIT
- Language: TypeScript (93.9%)
