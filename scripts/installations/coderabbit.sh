#!/usr/bin/env bash
# CodeRabbit — AI-powered code review
#
# What this does:
#   1. Creates .coderabbit.yaml config (review settings, language hints)
#   2. Verifies retry workflow exists
#   3. No API key needed — CodeRabbit uses GitHub App auth
#
# Free tier: Open source projects
# Dashboard: https://app.coderabbit.ai

set -euo pipefail

CONFIG=".coderabbit.yaml"

echo "=== CodeRabbit AI ==="
echo ""

# 1. Create config
if [ ! -f "$CONFIG" ]; then
    echo "→ Creating $CONFIG..."
    cat > "$CONFIG" << 'YAML'
# CodeRabbit configuration
# Docs: https://docs.coderabbit.ai/getting-started/configure-coderabbit

language: en-US

reviews:
  # Auto-review every PR
  auto_review:
    enabled: true
    # Skip draft PRs
    drafts: false
    # Review on these base branches
    base_branches:
      - main

  # Review profile: assertive catches more issues
  profile: assertive

  # High-level summary at top of review
  request_changes_workflow: true

  # Path-based instructions
  path_instructions:
    - path: "src/models/**"
      instructions: "Check Pydantic v2 patterns, model_validator usage, enum consistency"
    - path: "src/db/**"
      instructions: "Check async SQLAlchemy patterns, connection handling, SQL injection"
    - path: "app/**"
      instructions: "Check Next.js server component patterns, Drizzle query correctness"
    - path: "semantic/**"
      instructions: "Validate YAML schema consistency with Python models and Drizzle schema"
    - path: "tests/**"
      instructions: "Check test coverage, mock patterns, edge cases"

chat:
  # Allow @coderabbitai mentions in PR comments
  auto_reply: true

# Files to skip
path_filters:
  - "!docs/references/**"
  - "!research/**"
  - "!migrations/**"
  - "!.venv/**"
  - "!node_modules/**"
YAML
    echo "  ✓ Created $CONFIG"
else
    echo "  ✓ $CONFIG already exists"
fi

echo ""

# 2. Check retry workflow
RETRY=".github/workflows/coderabbit.yml"
if [ -f "$RETRY" ]; then
    echo "✓ Retry workflow: $RETRY"
else
    echo "✗ Missing retry workflow: $RETRY"
fi

echo ""
echo "→ How it works:"
echo "  - Every PR gets an AI review comment automatically"
echo "  - @coderabbitai in a comment to ask follow-up questions"
echo "  - Rate-limited reviews auto-retry via coderabbit.yml workflow"
echo ""
echo "=== CodeRabbit setup complete ==="
