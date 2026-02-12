# Claude Code Action with OAuth (Community Fork)

> Source: https://github.com/marketplace/actions/claude-code-action-with-oauth
> Fork by: grll/claude-code-action@beta
> Fetched: 2026-02-11
> Status: Fork marked obsolete after Anthropic added native support, but OAuth
>         auto-refresh pattern is still useful for Claude Max subscribers.

## Overview

Fork of Anthropic's official Claude Code Action that adds OAuth authentication support
for **Claude Max subscribers**. Use your Claude subscription directly in GitHub Actions
without needing API keys.

## OAuth vs API Key

| Method | Credential | Best for |
|--------|-----------|----------|
| API Key | `ANTHROPIC_API_KEY` | Orgs with API billing |
| OAuth | Access + refresh tokens from `~/.claude/.credentials.json` | Claude Max subscribers |

**Key difference:** OAuth uses your existing subscription. API keys are separate billable credentials.

## Required Secrets (OAuth mode)

| Secret | Source | Purpose |
|--------|--------|---------|
| `CLAUDE_ACCESS_TOKEN` | `~/.claude/.credentials.json` → `accessToken` | OAuth access token |
| `CLAUDE_REFRESH_TOKEN` | `~/.claude/.credentials.json` → `refreshToken` | Auto-refresh expired tokens |
| `CLAUDE_EXPIRES_AT` | `~/.claude/.credentials.json` → `expiresAt` | Token expiry timestamp |
| `SECRETS_ADMIN_PAT` | GitHub PAT with `secrets:write` | Lets action update expired secrets |

### Finding Your Credentials

```bash
# Linux/WSL:
cat ~/.claude/.credentials.json | python3 -m json.tool

# Fields:
# {
#   "accessToken": "...",
#   "refreshToken": "...",
#   "expiresAt": "2026-02-12T..."
# }
```

## Workflow YAML (OAuth)

```yaml
name: Claude PR Assistant

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

jobs:
  claude-code-action:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: read
      issues: read
      id-token: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Run Claude PR Action
        uses: grll/claude-code-action@beta
        with:
          use_oauth: true
          claude_access_token: ${{ secrets.CLAUDE_ACCESS_TOKEN }}
          claude_refresh_token: ${{ secrets.CLAUDE_REFRESH_TOKEN }}
          claude_expires_at: ${{ secrets.CLAUDE_EXPIRES_AT }}
          secrets_admin_pat: ${{ secrets.SECRETS_ADMIN_PAT }}
          timeout_minutes: "60"
```

## Automatic Token Refresh

1. **Before each run:** Checks if `claude_expires_at` has passed
2. **If expired:** Uses `claude_refresh_token` to get a new access token
3. **Updates secrets:** `secrets_admin_pat` allows the action to write fresh tokens back to repo secrets
4. **Seamless:** Subsequent runs use the refreshed tokens automatically

OAuth tokens are typically short-lived (hours). Without auto-refresh, workflows fail after expiration.

## Setup Steps

1. Install Claude GitHub app: https://github.com/apps/claude
2. Extract credentials from `~/.claude/.credentials.json`
3. Add 4 secrets to repo: `CLAUDE_ACCESS_TOKEN`, `CLAUDE_REFRESH_TOKEN`, `CLAUDE_EXPIRES_AT`, `SECRETS_ADMIN_PAT`
4. Add workflow file
5. Commit and push
