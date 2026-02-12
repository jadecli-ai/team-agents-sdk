#!/usr/bin/env bash
# Claude Code GitHub App — OAuth setup + workflow verification
#
# What this does:
#   1. Checks ~/.claude/.credentials.json exists (Claude Max OAuth)
#   2. Syncs OAuth tokens to repo secrets (CLAUDE_ACCESS_TOKEN, etc.)
#   3. Checks for SECRETS_ADMIN_PAT (needed for auto-refresh)
#   4. Verifies .github/workflows/claude.yml exists
#   5. Creates "claude-implement" label for issue→PR automation
#
# Docs: docs/references/claude-code-action-oauth.md

set -euo pipefail

REPO="${GITHUB_REPO:-jadecli-ai/team-agents-sdk}"
CREDS="$HOME/.claude/.credentials.json"
WORKFLOW=".github/workflows/claude.yml"

echo "=== Claude Code GitHub App ==="
echo ""

# 1. Check credentials
if [ -f "$CREDS" ]; then
    echo "✓ Credentials found: $CREDS"
    python3 -c "
import json, time
with open('$CREDS') as f:
    c = json.load(f)
oauth = c.get('claudeAiOauth', c)
sub = oauth.get('subscriptionType', 'unknown')
tier = oauth.get('rateLimitTier', 'unknown')
expires = int(oauth.get('expiresAt', 0)) / 1000
remaining = (expires - time.time()) / 3600
status = f'{remaining:.1f}h remaining' if remaining > 0 else f'EXPIRED {-remaining:.1f}h ago'
print(f'  Subscription: {sub} ({tier})')
print(f'  Token: {status}')
"
else
    echo "✗ No credentials at $CREDS"
    echo "  Run: claude (to authenticate)"
    exit 1
fi

echo ""

# 2. Sync OAuth tokens
echo "→ Syncing OAuth tokens to $REPO..."
ACCESS_TOKEN=$(python3 -c "import json; c=json.load(open('$CREDS')); o=c.get('claudeAiOauth',c); print(o['accessToken'])")
REFRESH_TOKEN=$(python3 -c "import json; c=json.load(open('$CREDS')); o=c.get('claudeAiOauth',c); print(o['refreshToken'])")
EXPIRES_AT=$(python3 -c "import json; c=json.load(open('$CREDS')); o=c.get('claudeAiOauth',c); print(o['expiresAt'])")

echo "$ACCESS_TOKEN" | gh secret set CLAUDE_ACCESS_TOKEN --repo "$REPO" 2>/dev/null && echo "  ✓ CLAUDE_ACCESS_TOKEN" || echo "  ✗ CLAUDE_ACCESS_TOKEN (repo may not exist yet)"
echo "$REFRESH_TOKEN" | gh secret set CLAUDE_REFRESH_TOKEN --repo "$REPO" 2>/dev/null && echo "  ✓ CLAUDE_REFRESH_TOKEN" || echo "  ✗ CLAUDE_REFRESH_TOKEN"
echo "$EXPIRES_AT" | gh secret set CLAUDE_EXPIRES_AT --repo "$REPO" 2>/dev/null && echo "  ✓ CLAUDE_EXPIRES_AT" || echo "  ✗ CLAUDE_EXPIRES_AT"

echo ""

# 3. Check SECRETS_ADMIN_PAT
echo "→ Checking SECRETS_ADMIN_PAT..."
if gh secret list --repo "$REPO" 2>/dev/null | grep -q SECRETS_ADMIN_PAT; then
    echo "  ✓ SECRETS_ADMIN_PAT is set (enables auto-refresh)"
else
    echo "  ✗ SECRETS_ADMIN_PAT not set"
    echo "  Create a fine-grained PAT at: https://github.com/settings/personal-access-tokens/new"
    echo "    → Resource owner: jadecli-ai"
    echo "    → Repository: team-agents-sdk"
    echo "    → Permissions: Secrets (read/write)"
    echo "  Then: gh secret set SECRETS_ADMIN_PAT --repo $REPO"
fi

echo ""

# 4. Check workflow
if [ -f "$WORKFLOW" ]; then
    echo "✓ Workflow exists: $WORKFLOW"
    echo "  Modes: OAuth (primary) → API key (fallback)"
else
    echo "✗ Workflow missing: $WORKFLOW"
fi

echo ""

# 5. Create claude-implement label
echo "→ Creating 'claude-implement' label..."
gh label create "claude-implement" \
    --repo "$REPO" \
    --description "Label an issue for Claude to auto-implement as a PR" \
    --color "7C3AED" \
    2>/dev/null && echo "  ✓ Label created" || echo "  ✓ Label already exists (or repo not ready)"

echo ""
echo "=== Claude setup complete ==="
