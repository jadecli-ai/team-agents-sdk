#!/usr/bin/env bash
# Vercel — Deploy Next.js dashboard to jadecli.com
#
# What this does:
#   1. Links project to Vercel (interactive on first run)
#   2. Pulls env vars from Vercel to local .env
#   3. Verifies Neon integration (auto-injects POSTGRES_URL)
#   4. Checks domain configuration
#
# Free tier: Hobby plan (1 project, preview deploys)
# Dashboard: https://vercel.com/jadecli-ai

set -euo pipefail

REPO="${GITHUB_REPO:-jadecli-ai/team-agents-sdk}"

echo "=== Vercel ==="
echo ""

# 1. Check auth
echo "→ Checking Vercel auth..."
if npx vercel whoami 2>/dev/null; then
    echo "  ✓ Authenticated"
else
    echo "  ✗ Not authenticated"
    echo "  Run: npx vercel login"
    exit 1
fi

echo ""

# 2. Link project (if not already linked)
if [ -d ".vercel" ]; then
    echo "✓ Project already linked"
    cat .vercel/project.json 2>/dev/null | python3 -m json.tool 2>/dev/null || true
else
    echo "→ Linking project to Vercel..."
    echo "  This will ask you to select/create a Vercel project."
    npx vercel link
fi

echo ""

# 3. Pull env vars
echo "→ Pulling environment variables from Vercel..."
npx vercel env pull .env.vercel 2>/dev/null && {
    echo "  ✓ Pulled to .env.vercel"
    echo "  Keys found:"
    grep -c '=' .env.vercel 2>/dev/null | xargs -I{} echo "    {} variables"
} || echo "  ✗ Could not pull (project may not be linked yet)"

echo ""

# 4. Check for Neon integration
echo "→ Checking for POSTGRES_URL (Neon integration)..."
if [ -f ".env.vercel" ] && grep -q "POSTGRES_URL" .env.vercel; then
    echo "  ✓ POSTGRES_URL found (Neon integration active)"
else
    echo "  ✗ POSTGRES_URL not found"
    echo "  Install Neon on Vercel: https://vercel.com/marketplace/neon"
    echo "  Then re-run: ./scripts/installations/vercel.sh"
fi

echo ""

# 5. Domain check
echo "→ Checking domains..."
npx vercel domains ls 2>/dev/null || echo "  (run after project is linked)"

echo ""
echo "→ Deploy commands:"
echo "  make deploy-preview   # Preview deploy"
echo "  make deploy           # Production deploy to jadecli.com"
echo ""
echo "→ GitHub App integration:"
echo "  - Every PR gets a preview deploy URL automatically"
echo "  - Merge to main triggers production deploy"
echo "  - No workflow needed — Vercel GitHub App handles it"
echo ""
echo "=== Vercel setup complete ==="
