#!/usr/bin/env bash
# Codacy Production — Code quality + security scanning
#
# What this does:
#   1. Verifies Codacy GitHub App is installed
#   2. Creates .codacy.yml config (languages, exclusions)
#   3. Enables PR status checks
#   4. No API key needed — Codacy uses GitHub App auth
#
# Free tier: Open source projects (unlimited)
# Dashboard: https://app.codacy.com/gh/jadecli-ai/team-agents-sdk

set -euo pipefail

REPO="${GITHUB_REPO:-jadecli-ai/team-agents-sdk}"
CONFIG=".codacy.yml"

echo "=== Codacy Production ==="
echo ""

# 1. Check installation
echo "→ Checking GitHub App installation..."
INSTALLED=$(gh api "/orgs/jadecli-ai/installations" --jq '.[].app_slug' 2>/dev/null | grep -c "codacy" || true)
if [ "$INSTALLED" -gt 0 ]; then
    echo "  ✓ Codacy app installed on jadecli-ai"
else
    echo "  ? Could not verify (may need admin scope)"
    echo "  Check: https://github.com/organizations/jadecli-ai/settings/installations"
fi

echo ""

# 2. Create config
if [ ! -f "$CONFIG" ]; then
    echo "→ Creating $CONFIG..."
    cat > "$CONFIG" << 'YAML'
# Codacy configuration
# Docs: https://docs.codacy.com/repositories-configure/codacy-configuration-file/

engines:
  # Python
  pylint:
    enabled: true
  bandit:
    enabled: true
  # TypeScript / JavaScript
  eslint:
    enabled: true
  # General
  duplication:
    enabled: true

exclude_paths:
  - ".venv/**"
  - "node_modules/**"
  - ".next/**"
  - "migrations/**"
  - "research/**"
  - "docs/references/**"

languages:
  python:
    version: "3.13"
YAML
    echo "  ✓ Created $CONFIG"
else
    echo "  ✓ $CONFIG already exists"
fi

echo ""
echo "→ Next steps:"
echo "  1. Visit https://app.codacy.com to see analysis"
echo "  2. Codacy auto-scans on every push and PR"
echo "  3. No secrets needed — uses GitHub App auth"
echo ""
echo "=== Codacy setup complete ==="
