#!/bin/bash
# secrets-setup.sh — Set up Bitwarden Secrets Manager for JadeCLI
#
# Prerequisites:
#   1. Sign up at https://vault.bitwarden.com/#/register (FREE)
#   2. Create an Organization (free for 2 users)
#   3. Enable Secrets Manager for the org
#   4. Create a Machine Account + Access Token
#   5. Export: BWS_ACCESS_TOKEN=<token>
#
# Usage:
#   bash scripts/secrets-setup.sh          # Create all secrets from env.template
#   bash scripts/secrets-setup.sh --check  # Verify secrets exist
#   bash scripts/secrets-setup.sh --sync   # Sync .env -> Bitwarden

set -euo pipefail

BWS="${HOME}/.local/bin/bws"
PROJECT_ID=""  # Set after creating project

# ── Colors ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}  ✓ $1${NC}"; }
fail() { echo -e "${RED}  ✗ $1${NC}"; }
warn() { echo -e "${YELLOW}  ⚠ $1${NC}"; }
info() { echo -e "  → $1"; }

# ── Preflight ──
check_prereqs() {
    echo "=== Bitwarden Secrets Manager Setup ==="
    echo ""

    if ! command -v bws &>/dev/null; then
        fail "bws CLI not found. Install: gh release download bws-v2.0.0 --repo bitwarden/sdk-sm"
        exit 1
    fi
    pass "bws $(bws --version) installed"

    if [ -z "${BWS_ACCESS_TOKEN:-}" ]; then
        fail "BWS_ACCESS_TOKEN not set"
        echo ""
        echo "  To get an access token:"
        echo "    1. Go to https://vault.bitwarden.com"
        echo "    2. Organization > Secrets Manager > Machine Accounts"
        echo "    3. Create a Machine Account for 'jadecli-agents'"
        echo "    4. Generate an Access Token"
        echo "    5. export BWS_ACCESS_TOKEN=<token>"
        exit 1
    fi
    pass "BWS_ACCESS_TOKEN is set"
}

# ── Create Project ──
create_project() {
    info "Creating project 'jadecli-team-agents-sdk'..."
    PROJECT_ID=$(bws project create jadecli-team-agents-sdk 2>/dev/null | jq -r '.id' 2>/dev/null || echo "")
    if [ -n "$PROJECT_ID" ]; then
        pass "Project created: $PROJECT_ID"
    else
        warn "Project may already exist. Listing projects..."
        PROJECT_ID=$(bws project list 2>/dev/null | jq -r '.[] | select(.name=="jadecli-team-agents-sdk") | .id' 2>/dev/null || echo "")
        if [ -n "$PROJECT_ID" ]; then
            pass "Found existing project: $PROJECT_ID"
        else
            fail "Could not create or find project"
            exit 1
        fi
    fi
}

# ── Sync .env to Bitwarden ──
sync_env() {
    local env_file="${1:-.env}"
    if [ ! -f "$env_file" ]; then
        fail "No .env file found at $env_file"
        exit 1
    fi

    info "Syncing $env_file to Bitwarden Secrets Manager..."
    local count=0

    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        # Strip surrounding whitespace
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        # Skip empty values
        [ -z "$value" ] && continue

        # Create or update secret
        if bws secret create "$key" "$value" --project-id "$PROJECT_ID" &>/dev/null; then
            pass "$key"
            ((count++))
        else
            warn "$key (may already exist, updating...)"
            # Try to find and update
            local secret_id
            secret_id=$(bws secret list --project-id "$PROJECT_ID" 2>/dev/null | jq -r ".[] | select(.key==\"$key\") | .id" 2>/dev/null || echo "")
            if [ -n "$secret_id" ]; then
                bws secret edit "$secret_id" --value "$value" &>/dev/null && pass "$key (updated)" || fail "$key"
            fi
        fi
    done < "$env_file"

    echo ""
    pass "Synced $count secrets to Bitwarden"
}

# ── Check Secrets ──
check_secrets() {
    info "Checking secrets in project..."
    bws secret list --project-id "$PROJECT_ID" 2>/dev/null | jq -r '.[] | "  \(.key)"' 2>/dev/null || fail "Could not list secrets"
}

# ── Main ──
check_prereqs

case "${1:-}" in
    --check)
        create_project
        check_secrets
        ;;
    --sync)
        create_project
        sync_env "${2:-.env}"
        ;;
    *)
        echo ""
        echo "Usage:"
        echo "  $0          # Show setup instructions"
        echo "  $0 --sync   # Sync .env to Bitwarden"
        echo "  $0 --check  # List stored secrets"
        echo ""
        echo "Once configured, run CLI tools with secrets:"
        echo "  bws run 'claude --print \"hello\"' --project-id <id>"
        echo "  bws run 'gemini' --project-id <id>"
        echo ""
        echo "Or export to current shell:"
        echo "  eval \$(bws secret list --project-id <id> | jq -r '.[] | \"export \\(.key)=\\(.value)\"')"
        ;;
esac
