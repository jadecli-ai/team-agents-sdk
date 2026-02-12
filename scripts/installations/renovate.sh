#!/usr/bin/env bash
# Renovate — Automated dependency updates
#
# What this does:
#   1. Creates renovate.json config (grouping, scheduling, automerge rules)
#   2. No API key needed — Renovate uses GitHub App auth
#
# Free tier: Fully free (AGPL open source)
# Dashboard: https://developer.mend.io/

set -euo pipefail

CONFIG="renovate.json"

echo "=== Renovate ==="
echo ""

if [ ! -f "$CONFIG" ]; then
    echo "→ Creating $CONFIG..."
    cat > "$CONFIG" << 'JSON'
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:recommended",
    ":semanticCommits",
    ":automergeMinor",
    "schedule:weekends"
  ],
  "labels": ["dependencies"],
  "rangeStrategy": "bump",
  "packageRules": [
    {
      "description": "Group Python deps",
      "matchManagers": ["pip_requirements", "pep621"],
      "groupName": "python dependencies",
      "automerge": false
    },
    {
      "description": "Group Node deps",
      "matchManagers": ["npm"],
      "groupName": "node dependencies",
      "automerge": false
    },
    {
      "description": "Automerge patch updates for dev deps",
      "matchDepTypes": ["devDependencies"],
      "matchUpdateTypes": ["patch"],
      "automerge": true
    },
    {
      "description": "Automerge GitHub Actions minor/patch",
      "matchManagers": ["github-actions"],
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    },
    {
      "description": "Pin Claude Agent SDK to minor",
      "matchPackageNames": ["claude-agent-sdk"],
      "rangeStrategy": "bump",
      "automerge": false
    }
  ],
  "vulnerabilityAlerts": {
    "enabled": true,
    "labels": ["security"]
  }
}
JSON
    echo "  ✓ Created $CONFIG"
else
    echo "  ✓ $CONFIG already exists"
fi

echo ""
echo "→ How it works:"
echo "  - Renovate creates PRs for dependency updates on weekends"
echo "  - Dev dep patches automerge"
echo "  - GitHub Actions minor/patch automerge"
echo "  - Python and Node deps grouped into single PRs"
echo "  - Security vulns get immediate PRs with 'security' label"
echo ""
echo "=== Renovate setup complete ==="
