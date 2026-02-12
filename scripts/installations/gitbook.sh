#!/usr/bin/env bash
# GitBook — Documentation platform synced from GitHub
#
# What this does:
#   1. Creates docs/ structure for GitBook sync
#   2. Creates SUMMARY.md (GitBook table of contents)
#   3. No API key needed — GitBook uses GitHub App auth
#
# Free tier: 1 space, public docs
# Dashboard: https://app.gitbook.com

set -euo pipefail

echo "=== GitBook ==="
echo ""

# 1. Ensure docs structure
mkdir -p docs

if [ ! -f "docs/SUMMARY.md" ]; then
    echo "→ Creating docs/SUMMARY.md (GitBook table of contents)..."
    cat > docs/SUMMARY.md << 'MD'
# Table of Contents

## Getting Started

* [Overview](README.md)
* [Setup](setup.md)
* [Makefile Reference](makefile.md)

## Architecture

* [Semantic Schema](architecture/semantic-schema.md)
* [Database Layer](architecture/database.md)
* [Agent Hooks](architecture/hooks.md)

## API Reference

* [Pydantic Models](api/models.md)
* [CRUD Operations](api/crud.md)
* [GitHub Sync](api/github-sync.md)

## References

* [Claude Code Action](references/claude-code-action-official.md)
* [Claude OAuth Setup](references/claude-code-action-oauth.md)
* [Codacy](references/codacy.md)
* [CodeRabbit](references/coderabbit-retry-action.md)
* [GitHub Apps](references/github-apps-research.md)
MD
    echo "  ✓ Created docs/SUMMARY.md"
else
    echo "  ✓ docs/SUMMARY.md already exists"
fi

if [ ! -f "docs/README.md" ]; then
    echo "→ Creating docs/README.md..."
    cat > docs/README.md << 'MD'
# jadecli-team-agents-sdk

Multi-agent task system with Neon Postgres, Claude Agent SDK, and MLflow tracing.

## Quick Start

```bash
make install    # Install Python + Node deps
make test       # Run all tests
make dev        # Start Next.js dev server
```

## Stack

| Component | Purpose |
|-----------|---------|
| Semantic YAML | Single source of truth for schemas |
| Pydantic v2 | Python models with validators |
| SQLAlchemy + asyncpg | Async Neon Postgres access |
| Drizzle ORM | TypeScript schema for Next.js |
| Claude Agent SDK | Multi-agent orchestration |
| MLflow 3.9 | Tracing and evaluation |
MD
    echo "  ✓ Created docs/README.md"
else
    echo "  ✓ docs/README.md already exists"
fi

echo ""
echo "→ GitBook sync:"
echo "  1. Visit https://app.gitbook.com → Create space"
echo "  2. Integrations → GitHub → Select jadecli-ai/team-agents-sdk"
echo "  3. Set sync directory to: docs/"
echo "  4. Branch: main"
echo "  5. GitBook auto-publishes on every push to main"
echo ""
echo "=== GitBook setup complete ==="
