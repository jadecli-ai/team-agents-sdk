#!/usr/bin/env bash
# Sync Claude OAuth credentials from local ~/.claude/.credentials.json to GitHub repo secrets.
# This enables the Claude Code Action to use your Claude Max subscription (no API key needed).
#
# Usage:
#   ./scripts/sync-claude-oauth.sh                    # uses current gh repo context
#   ./scripts/sync-claude-oauth.sh jadecli-ai/team-agents-sdk   # explicit repo
#
# What it does:
#   1. Reads accessToken, refreshToken, expiresAt from ~/.claude/.credentials.json
#   2. Sets CLAUDE_ACCESS_TOKEN, CLAUDE_REFRESH_TOKEN, CLAUDE_EXPIRES_AT as repo secrets
#   3. Never prints token values — only status

set -euo pipefail

CREDS_FILE="${HOME}/.claude/.credentials.json"
REPO="${1:-}"

if [ ! -f "$CREDS_FILE" ]; then
    echo "ERROR: $CREDS_FILE not found. Log in with: claude"
    exit 1
fi

# Extract values using Python (jq not always available on WSL)
read -r ACCESS_TOKEN REFRESH_TOKEN EXPIRES_AT <<< "$(python3 -c "
import json, sys
with open('$CREDS_FILE') as f:
    c = json.load(f)
oauth = c.get('claudeAiOauth', c)
print(oauth['accessToken'], oauth['refreshToken'], oauth['expiresAt'])
")"

if [ -z "$ACCESS_TOKEN" ] || [ -z "$REFRESH_TOKEN" ]; then
    echo "ERROR: Could not extract tokens from $CREDS_FILE"
    exit 1
fi

# Check expiry
python3 -c "
import time
expires = int('$EXPIRES_AT') / 1000
remaining = expires - time.time()
hours = remaining / 3600
if hours < 0:
    print(f'  WARNING: Token expired {-hours:.1f}h ago. Run: claude (to refresh)')
else:
    print(f'  Token expires in {hours:.1f}h')
"

# Build gh flags
GH_FLAGS=""
if [ -n "$REPO" ]; then
    GH_FLAGS="--repo $REPO"
fi

echo "→ Setting CLAUDE_ACCESS_TOKEN..."
echo "$ACCESS_TOKEN" | gh secret set CLAUDE_ACCESS_TOKEN $GH_FLAGS
echo "→ Setting CLAUDE_REFRESH_TOKEN..."
echo "$REFRESH_TOKEN" | gh secret set CLAUDE_REFRESH_TOKEN $GH_FLAGS
echo "→ Setting CLAUDE_EXPIRES_AT..."
echo "$EXPIRES_AT" | gh secret set CLAUDE_EXPIRES_AT $GH_FLAGS

echo ""
echo "✓ Claude OAuth secrets synced to GitHub."
echo "  The workflow will auto-refresh tokens when they expire."
echo "  Subscription: Claude Max (rate_limit: default_claude_max_20x)"
