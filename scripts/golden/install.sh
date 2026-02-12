#!/usr/bin/env bash
# Golden WSL2 distro master installer — runs all phases in order.
#
# Usage:
#   sudo ./install.sh          # Install everything
#   sudo ./install.sh --phase 1  # Run specific phase only
#
# Phases:
#   1: sysctl tunings
#   2: Docker daemon config
#   3: MLflow config + systemd timer
#   4: Tailscale install
#   5: Install bin scripts + health check
#   6: Install MCP configs
#   7: Modern CLI tools (Rust, cargo, binary releases, shell integration)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PHASE="${2:-all}"

BOLD='\033[1m'
GREEN='\033[0;32m'
NC='\033[0m'

run_phase() {
    local num="$1"
    local desc="$2"
    if [[ "$PHASE" != "all" && "$PHASE" != "$num" ]]; then
        return
    fi
    echo ""
    echo -e "${BOLD}=== Phase $num: $desc ===${NC}"
}

# ── Phase 1: sysctl ─────────────────────────────────────────────────
run_phase 1 "sysctl tunings"
if [[ "$PHASE" == "all" || "$PHASE" == "1" ]]; then
    cp "$SCRIPT_DIR/configs/99-golden.conf" /etc/sysctl.d/99-golden.conf
    sysctl --system > /dev/null
    echo -e "  ${GREEN}sysctl tunings applied${NC}"
    echo "  vm.swappiness=$(sysctl -n vm.swappiness)"
fi

# ── Phase 2: Docker ──────────────────────────────────────────────────
run_phase 2 "Docker daemon config"
if [[ "$PHASE" == "all" || "$PHASE" == "2" ]]; then
    cp "$SCRIPT_DIR/configs/daemon.json" /etc/docker/daemon.json
    systemctl restart docker 2>/dev/null || echo "  Docker restart skipped (not running)"
    echo -e "  ${GREEN}daemon.json installed${NC}"
fi

# ── Phase 3: MLflow ──────────────────────────────────────────────────
run_phase 3 "MLflow config + systemd timer"
if [[ "$PHASE" == "all" || "$PHASE" == "3" ]]; then
    mkdir -p /etc/mlflow
    cp "$SCRIPT_DIR/configs/clone.env" /etc/mlflow/clone.env
    cp "$SCRIPT_DIR/configs/neon.env.example" /etc/mlflow/neon.env.example

    # Systemd units
    cp "$SCRIPT_DIR/systemd/mlflow-sync.service" /etc/systemd/system/
    cp "$SCRIPT_DIR/systemd/mlflow-sync.timer" /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable mlflow-sync.timer
    systemctl start mlflow-sync.timer 2>/dev/null || true
    echo -e "  ${GREEN}MLflow config + timer installed${NC}"
fi

# ── Phase 4: Tailscale ───────────────────────────────────────────────
run_phase 4 "Tailscale install"
if [[ "$PHASE" == "all" || "$PHASE" == "4" ]]; then
    if command -v tailscale &>/dev/null; then
        echo "  Tailscale already installed"
    else
        curl -fsSL https://tailscale.com/install.sh | sh
        echo -e "  ${GREEN}Tailscale installed${NC}"
    fi
    # Copy tailscale env
    cp "$SCRIPT_DIR/configs/tailscale.env" /etc/mlflow/tailscale.env 2>/dev/null || true
fi

# ── Phase 5: Bin scripts ────────────────────────────────────────────
run_phase 5 "Install bin scripts"
if [[ "$PHASE" == "all" || "$PHASE" == "5" ]]; then
    for script in "$SCRIPT_DIR/bin/"*; do
        local name
        name="$(basename "$script")"
        cp "$script" "/usr/local/bin/$name"
        chmod +x "/usr/local/bin/$name"
        echo "  Installed /usr/local/bin/$name"
    done
    echo -e "  ${GREEN}All bin scripts installed${NC}"
fi

# ── Phase 6: MCP configs ────────────────────────────────────────────
run_phase 6 "MCP configs"
if [[ "$PHASE" == "all" || "$PHASE" == "6" ]]; then
    mkdir -p /usr/local/share/golden/configs/mcp
    cp "$SCRIPT_DIR/configs/mcp/"*.json /usr/local/share/golden/configs/mcp/
    echo -e "  ${GREEN}MCP configs installed to /usr/local/share/golden/configs/mcp/${NC}"
fi

# ── Phase 7: CLI tools ──────────────────────────────────────────────
run_phase 7 "Modern CLI tools"
if [[ "$PHASE" == "all" || "$PHASE" == "7" ]]; then
    # Run as the regular user, not root (cargo install needs user home)
    REAL_USER="${SUDO_USER:-org-jadecli}"
    if [[ "$(whoami)" == "root" && -n "$REAL_USER" ]]; then
        su - "$REAL_USER" -c "bash $SCRIPT_DIR/install-cli-tools.sh"
    else
        bash "$SCRIPT_DIR/install-cli-tools.sh"
    fi
    echo -e "  ${GREEN}CLI tools installed${NC}"
fi

# ── Done ─────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}Golden image setup complete.${NC}"
echo ""
echo "Next steps:"
echo "  1. Run 'distro-health-check' to verify"
echo "  2. Run 'distro-benchmark' for baseline performance"
echo "  3. For cloning: 'golden-cleanup' then 'wsl --export'"
echo "  4. After import: 'clone-init <name>' to initialize"
