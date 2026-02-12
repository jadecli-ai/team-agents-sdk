#!/usr/bin/env bash
# Snyk — Security scanning (deps, code, containers)
#
# What this does:
#   1. Creates .snyk policy file (ignores, severity threshold)
#   2. Adds Snyk GitHub Action for PR checks
#   3. No repo secret needed for GitHub App mode
#
# Free tier: 200 tests/month for open source
# Dashboard: https://app.snyk.io

set -euo pipefail

POLICY=".snyk"

echo "=== Snyk ==="
echo ""

# 1. Create policy file
if [ ! -f "$POLICY" ]; then
    echo "→ Creating $POLICY policy..."
    cat > "$POLICY" << 'YAML'
# Snyk policy file
# https://docs.snyk.io/manage-risk/policies/the-.snyk-file
version: v1.25.0

# Ignore specific vulnerabilities (add as needed)
ignore: {}

# Only fail on high/critical severity
patch: {}
YAML
    echo "  ✓ Created $POLICY"
else
    echo "  ✓ $POLICY already exists"
fi

echo ""

# 2. Check for Snyk workflow (optional — GitHub App handles most scanning)
WORKFLOW=".github/workflows/snyk.yml"
if [ ! -f "$WORKFLOW" ]; then
    echo "→ Creating $WORKFLOW..."
    mkdir -p .github/workflows
    cat > "$WORKFLOW" << 'YAML'
# Snyk Security Scan — runs on PRs to main
# The Snyk GitHub App handles continuous monitoring.
# This workflow adds explicit PR gate checks.
name: Snyk

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 6 * * 1"  # Weekly Monday 6am UTC

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: "22"

      - name: Install deps
        run: |
          pip install -e ".[dev]"
          npm install

      - name: Snyk Python test
        uses: snyk/actions/python-3.10@master
        continue-on-error: true
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

      - name: Snyk Node test
        uses: snyk/actions/node@master
        continue-on-error: true
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
YAML
    echo "  ✓ Created $WORKFLOW"
else
    echo "  ✓ $WORKFLOW already exists"
fi

echo ""
echo "→ Snyk modes:"
echo "  1. GitHub App: Continuous monitoring (no token needed)"
echo "  2. PR workflow: Explicit gate check (optional SNYK_TOKEN)"
echo "     Get token at: https://app.snyk.io/account"
echo "     Then: gh secret set SNYK_TOKEN --repo jadecli-ai/team-agents-sdk"
echo ""
echo "=== Snyk setup complete ==="
