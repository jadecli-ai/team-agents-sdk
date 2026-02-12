# CodeRabbit Retry Action

> Source: https://github.com/marketplace/actions/coderabbit-retry
> Fetched: 2026-02-11

## What It Does

Automatically retries CodeRabbit reviews when they fail due to rate limiting.
Monitors open PRs and requests re-reviews when:
- The latest commit lacks a CodeRabbit review
- A "Rate Limit exceeded" comment exists
- No retry has been attempted within the cooldown window

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `github-token` | Yes | — | GitHub token for API access |
| `max-retries` | No | 4 | Max retry attempts |
| `cooldown-hours` | No | 2 | Hours between retries |
| `dry-run` | No | false | Log without acting |
| `ignore-branches` | No | '' | Branches to skip |
| `ignore-labels` | No | '' | Labels to skip |

## Usage

```yaml
name: CodeRabbit Retry

on:
  schedule:
    - cron: '0 * * * *'  # Run every hour
  workflow_dispatch:

jobs:
  retry:
    runs-on: ubuntu-latest
    steps:
      - name: Retry CodeRabbit Reviews
        uses: idrinth/coderabbit-retry-action@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```
