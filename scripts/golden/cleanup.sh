#!/usr/bin/env bash
# Pre-export cleanup for golden WSL2 distro.
#
# Run this before 'wsl --export' to minimize image size.
# Removes caches, logs, secrets, and temporary data.
#
# Usage:
#   sudo ./cleanup.sh           # Full cleanup
#   sudo ./cleanup.sh --dry-run # Show what would be removed
set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

USER_HOME="/home/org-jadecli"

clean() {
    local desc="$1"
    shift
    if $DRY_RUN; then
        echo -e "  ${YELLOW}[dry-run]${NC} $desc"
        for target in "$@"; do
            [ -e "$target" ] && echo "    $target"
        done
    else
        echo "  $desc"
        for target in "$@"; do
            rm -rf "$target" 2>/dev/null || true
        done
    fi
}

echo -e "${BOLD}Golden WSL2 Pre-Export Cleanup${NC}"
echo ""

# ── Package caches ───────────────────────────────────────────────────
echo -e "${BOLD}Package caches${NC}"
if ! $DRY_RUN; then
    apt-get clean 2>/dev/null || true
    apt-get autoclean 2>/dev/null || true
fi
clean "apt cache" /var/cache/apt/archives/*.deb
clean "pip cache" "$USER_HOME/.cache/pip" /root/.cache/pip
clean "uv cache" "$USER_HOME/.cache/uv" /root/.cache/uv
clean "npm cache" "$USER_HOME/.npm/_cacache"
clean "node_modules caches" /tmp/npm-* /tmp/v8-*

# ── Docker cleanup ───────────────────────────────────────────────────
echo -e "${BOLD}Docker artifacts${NC}"
if docker info &>/dev/null && ! $DRY_RUN; then
    docker system prune -f 2>/dev/null || true
    echo "  Docker system prune complete"
else
    echo "  [skip] Docker not running"
fi

# ── Logs ─────────────────────────────────────────────────────────────
echo -e "${BOLD}Logs${NC}"
if ! $DRY_RUN; then
    journalctl --vacuum-time=1d 2>/dev/null || true
fi
clean "journal logs" /var/log/journal/*
clean "syslog" /var/log/syslog* /var/log/auth.log*
clean "apt logs" /var/log/apt/*
clean "health check log" /var/log/distro-health.log

# ── Temp files ───────────────────────────────────────────────────────
echo -e "${BOLD}Temporary files${NC}"
clean "system tmp" /tmp/* /var/tmp/*
clean "crash reports" /var/crash/*

# ── User-specific cleanup ────────────────────────────────────────────
echo -e "${BOLD}User data (sensitive)${NC}"
clean "bash history" "$USER_HOME/.bash_history" /root/.bash_history
clean "zsh history" "$USER_HOME/.zsh_history" "$USER_HOME/.zsh_sessions"
clean "python history" "$USER_HOME/.python_history"
clean "node repl history" "$USER_HOME/.node_repl_history"
clean "MLflow sync watermark" "$USER_HOME/.mlflow/sync_watermark"
clean "MLflow local DB" "$USER_HOME/.mlflow/mlruns.db"
clean "benchmark baseline" "$USER_HOME/.distro-baseline.json"

# Backup files (Claude Code)
clean "claude backup files" "$USER_HOME"/.claude.json.backup.*

# Empty placeholder directories
clean "empty azure dir" "$USER_HOME/.azure"
clean "empty aws dir" "$USER_HOME/.aws"
clean "empty dotnet dir" "$USER_HOME/.dotnet"
clean "empty copilot dir" "$USER_HOME/.copilot"
clean "vscode remote containers" "$USER_HOME/.vscode-remote-containers"

# Stale completion caches (zsh)
clean "zsh completion caches" "$USER_HOME"/.zcompdump*

# Cargo registry cache (recoverable — rebuilds on next install)
clean "cargo registry cache" "$USER_HOME/.cargo/registry/cache"

# Remove clone-specific secrets (neon.env has real creds)
clean "neon.env (creds)" /etc/mlflow/neon.env

# Reset clone identity to golden
if ! $DRY_RUN; then
    if [ -f /etc/mlflow/clone.env ]; then
        cat > /etc/mlflow/clone.env <<'EOF'
CLONE_ID=golden
CLONE_NAME=golden
CLONE_CREATED_AT=
EOF
        echo "  Reset clone.env to golden"
    fi
fi

# ── Summary ──────────────────────────────────────────────────────────
echo ""
if $DRY_RUN; then
    echo -e "${YELLOW}Dry run complete — no files were removed${NC}"
else
    echo -e "${GREEN}${BOLD}Cleanup complete.${NC}"
    echo ""
    echo "Ready to export:"
    echo "  wsl --shutdown"
    echo "  wsl --export Ubuntu-26.04-jadecli golden-$(date +%Y%m%d).tar"
fi
