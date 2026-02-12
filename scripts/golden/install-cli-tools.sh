#!/usr/bin/env bash
# Install modern CLI tools for golden WSL2 distro.
#
# Phases:
#   1: Rust toolchain (prerequisite for cargo installs)
#   2: Core CLI tools (apt + cargo + binary releases)
#   3: Shell integration (starship, zoxide, direnv, fzf, delta)
#   4: Python/Node tools (pipx, yq, aider, opencommit)
#
# Usage:
#   ./install-cli-tools.sh           # Install everything
#   ./install-cli-tools.sh --phase 2 # Run specific phase only
#   ./install-cli-tools.sh --check   # Verify what's installed
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PHASE="${2:-all}"
USER_HOME="${HOME:-/home/org-jadecli}"

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ── Parse args ──────────────────────────────────────────────────────
CHECK_ONLY=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --phase) PHASE="$2"; shift 2 ;;
        --check) CHECK_ONLY=true; shift ;;
        --help|-h)
            echo "Usage: install-cli-tools.sh [--phase N] [--check]"
            echo ""
            echo "Phases: 1 (Rust), 2 (CLI tools), 3 (shell), 4 (Python/Node)"
            exit 0
            ;;
        *) shift ;;
    esac
done

should_run() {
    [[ "$PHASE" == "all" || "$PHASE" == "$1" ]]
}

installed() {
    command -v "$1" &>/dev/null
}

# ── Check mode ──────────────────────────────────────────────────────
if $CHECK_ONLY; then
    echo -e "${BOLD}CLI Tools Status${NC}"
    echo ""

    tools=(
        "rustc:Rust compiler"
        "cargo:Cargo package manager"
        "batcat:bat (syntax highlighting)"
        "fdfind:fd (file finder)"
        "fzf:fzf (fuzzy finder)"
        "htop:htop (process viewer)"
        "direnv:direnv (per-dir env)"
        "duf:duf (disk usage)"
        "nvim:neovim"
        "eza:eza (modern ls)"
        "zoxide:zoxide (smart cd)"
        "sd:sd (find & replace)"
        "dust:dust (disk usage)"
        "tokei:tokei (code stats)"
        "procs:procs (process viewer)"
        "btm:bottom (system monitor)"
        "hyperfine:hyperfine (benchmarks)"
        "xh:xh (HTTP client)"
        "tldr:tealdeer (tldr pages)"
        "delta:delta (git diff)"
        "lazygit:lazygit (git TUI)"
        "lazydocker:lazydocker (docker TUI)"
        "starship:starship (prompt)"
        "yq:yq (YAML processor)"
        "pipx:pipx (Python tool installer)"
        "http:httpie (HTTP client)"
        "pre-commit:pre-commit (git hooks)"
    )

    ok=0
    missing=0
    for entry in "${tools[@]}"; do
        cmd="${entry%%:*}"
        desc="${entry##*:}"
        if installed "$cmd"; then
            echo -e "  ${GREEN}ok${NC}  $desc"
            ok=$((ok + 1))
        else
            echo -e "  ${RED}--${NC}  $desc"
            missing=$((missing + 1))
        fi
    done

    echo ""
    echo -e "${BOLD}Summary:${NC} ${GREEN}${ok} installed${NC}, ${RED}${missing} missing${NC}"
    exit 0
fi

echo -e "${BOLD}Golden WSL2 CLI Tools Installer${NC}"
echo ""

# ── Phase 1: Rust toolchain ────────────────────────────────────────
if should_run 1; then
    echo -e "${BOLD}=== Phase 1: Rust Toolchain ===${NC}"
    if installed rustc; then
        echo -e "  ${GREEN}Rust already installed${NC} ($(rustc --version))"
    else
        echo "  Installing Rust via rustup..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        # shellcheck source=/dev/null
        source "$USER_HOME/.cargo/env"
        echo -e "  ${GREEN}Rust installed${NC} ($(rustc --version))"
    fi
    echo ""
fi

# Ensure cargo is in PATH for subsequent phases
if [ -f "$USER_HOME/.cargo/env" ]; then
    # shellcheck source=/dev/null
    source "$USER_HOME/.cargo/env"
fi

# ── Phase 2: Core CLI tools ────────────────────────────────────────
if should_run 2; then
    echo -e "${BOLD}=== Phase 2: Core CLI Tools ===${NC}"

    # 2a. Via apt (fast, stable)
    echo "  [apt] Installing system packages..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq \
        bat fd-find fzf htop direnv duf neovim ripgrep \
        2>/dev/null || true
    echo -e "  ${GREEN}apt packages installed${NC}"

    # 2b. Via cargo (latest versions)
    if installed cargo; then
        echo "  [cargo] Installing Rust CLI tools (this may take ~15 min on first run)..."

        cargo_tools=(eza zoxide sd dust tokei procs bottom hyperfine xh tealdeer git-delta)
        for tool in "${cargo_tools[@]}"; do
            # Map cargo package name to binary name for skip check
            case "$tool" in
                bottom)    bin="btm" ;;
                tealdeer)  bin="tldr" ;;
                git-delta) bin="delta" ;;
                *)         bin="$tool" ;;
            esac
            if installed "$bin"; then
                echo -e "    ${GREEN}skip${NC}  $tool (already installed)"
            else
                echo "    install  $tool..."
                cargo install "$tool" --quiet 2>/dev/null || \
                    echo -e "    ${YELLOW}warn${NC}  $tool install failed"
            fi
        done
        echo -e "  ${GREEN}cargo tools installed${NC}"
    else
        echo -e "  ${YELLOW}cargo not found — skipping Rust CLI tools${NC}"
    fi

    # 2c. Via binary releases (Go tools)
    echo "  [binary] Installing Go-based tools..."

    # lazygit
    if installed lazygit; then
        echo -e "    ${GREEN}skip${NC}  lazygit (already installed)"
    else
        echo "    install  lazygit..."
        LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | jq -r '.tag_name' | sed 's/v//')
        if [[ -n "$LAZYGIT_VERSION" && "$LAZYGIT_VERSION" != "null" ]]; then
            curl -sLo /tmp/lazygit.tar.gz \
                "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
            tar xf /tmp/lazygit.tar.gz -C /tmp lazygit
            sudo install /tmp/lazygit /usr/local/bin/
            rm -f /tmp/lazygit /tmp/lazygit.tar.gz
            echo -e "    ${GREEN}lazygit installed${NC}"
        else
            echo -e "    ${YELLOW}warn${NC}  could not fetch lazygit version"
        fi
    fi

    # lazydocker
    if installed lazydocker; then
        echo -e "    ${GREEN}skip${NC}  lazydocker (already installed)"
    else
        echo "    install  lazydocker..."
        LAZYDOCKER_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazydocker/releases/latest" | jq -r '.tag_name' | sed 's/v//')
        if [[ -n "$LAZYDOCKER_VERSION" && "$LAZYDOCKER_VERSION" != "null" ]]; then
            curl -sLo /tmp/lazydocker.tar.gz \
                "https://github.com/jesseduffield/lazydocker/releases/latest/download/lazydocker_${LAZYDOCKER_VERSION}_Linux_x86_64.tar.gz"
            tar xf /tmp/lazydocker.tar.gz -C /tmp lazydocker
            sudo install /tmp/lazydocker /usr/local/bin/
            rm -f /tmp/lazydocker /tmp/lazydocker.tar.gz
            echo -e "    ${GREEN}lazydocker installed${NC}"
        else
            echo -e "    ${YELLOW}warn${NC}  could not fetch lazydocker version"
        fi
    fi

    # 2d. Starship prompt
    if installed starship; then
        echo -e "    ${GREEN}skip${NC}  starship (already installed)"
    else
        echo "    install  starship..."
        curl -sS https://starship.rs/install.sh | sh -s -- -y
        echo -e "    ${GREEN}starship installed${NC}"
    fi

    echo ""
fi

# ── Phase 3: Shell integration ─────────────────────────────────────
if should_run 3; then
    echo -e "${BOLD}=== Phase 3: Shell Integration ===${NC}"

    ZSHRC="$USER_HOME/.zshrc"
    GITCONFIG="$USER_HOME/.gitconfig"

    # Add CLI aliases to .zshrc if not already present
    MARKER="# ── Modern CLI aliases (golden) ──"
    if [ -f "$ZSHRC" ] && grep -qF "$MARKER" "$ZSHRC"; then
        echo -e "  ${GREEN}skip${NC}  .zshrc aliases already configured"
    else
        echo "  Adding CLI aliases to .zshrc..."
        cat >> "$ZSHRC" << 'ZSHRC_BLOCK'

# ── Modern CLI aliases (golden) ──
# bat (installed as batcat on Ubuntu)
if command -v batcat &>/dev/null; then
    alias bat='batcat'
    alias cat='batcat --paging=never'
fi

# fd (installed as fdfind on Ubuntu)
if command -v fdfind &>/dev/null; then
    alias fd='fdfind'
fi

# eza (modern ls replacement)
if command -v eza &>/dev/null; then
    alias ls='eza --icons --group-directories-first'
    alias ll='eza -la --icons --group-directories-first --git'
    alias tree='eza --tree --icons'
fi

# Starship prompt
if command -v starship &>/dev/null; then
    eval "$(starship init zsh)"
fi

# Zoxide (smart cd)
if command -v zoxide &>/dev/null; then
    eval "$(zoxide init zsh)"
fi

# Direnv (per-directory .envrc)
if command -v direnv &>/dev/null; then
    eval "$(direnv hook zsh)"
fi

# fzf key bindings + completion
if [ -f /usr/share/doc/fzf/examples/key-bindings.zsh ]; then
    source /usr/share/doc/fzf/examples/key-bindings.zsh
fi
if [ -f /usr/share/doc/fzf/examples/completion.zsh ]; then
    source /usr/share/doc/fzf/examples/completion.zsh
fi

# Delta as git pager
if command -v delta &>/dev/null; then
    export GIT_PAGER="delta"
fi

# Tealdeer config
export TEALDEER_CONFIG_DIR="$HOME/.config/tealdeer"
ZSHRC_BLOCK
        echo -e "  ${GREEN}.zshrc updated${NC}"
    fi

    # Add delta config to .gitconfig
    DELTA_MARKER="[delta]"
    if [ -f "$GITCONFIG" ] && grep -qF "$DELTA_MARKER" "$GITCONFIG"; then
        echo -e "  ${GREEN}skip${NC}  .gitconfig delta already configured"
    else
        echo "  Adding delta pager config to .gitconfig..."
        git config --global core.pager delta
        git config --global interactive.diffFilter "delta --color-only"
        git config --global delta.navigate true
        git config --global delta.side-by-side true
        git config --global delta.line-numbers true
        echo -e "  ${GREEN}.gitconfig updated${NC}"
    fi

    # Install starship config
    STARSHIP_DIR="$USER_HOME/.config"
    mkdir -p "$STARSHIP_DIR"
    if [ -f "$SCRIPT_DIR/configs/starship.toml" ] && [ ! -f "$STARSHIP_DIR/starship.toml" ]; then
        cp "$SCRIPT_DIR/configs/starship.toml" "$STARSHIP_DIR/starship.toml"
        echo -e "  ${GREEN}starship.toml installed${NC}"
    elif [ -f "$STARSHIP_DIR/starship.toml" ]; then
        echo -e "  ${GREEN}skip${NC}  starship.toml already exists"
    fi

    echo ""
fi

# ── Phase 4: Python/Node tools ─────────────────────────────────────
if should_run 4; then
    echo -e "${BOLD}=== Phase 4: Python/Node Tools ===${NC}"

    # pipx
    if installed pipx; then
        echo -e "  ${GREEN}skip${NC}  pipx (already installed)"
    else
        echo "  Installing pipx..."
        sudo apt-get install -y -qq pipx 2>/dev/null || pip install --user pipx
        pipx ensurepath 2>/dev/null || true
        echo -e "  ${GREEN}pipx installed${NC}"
    fi

    # httpie via pipx
    if installed http; then
        echo -e "  ${GREEN}skip${NC}  httpie (already installed)"
    else
        echo "  Installing httpie..."
        pipx install httpie 2>/dev/null || pip install --user httpie
        echo -e "  ${GREEN}httpie installed${NC}"
    fi

    # pre-commit via pipx
    if installed pre-commit; then
        echo -e "  ${GREEN}skip${NC}  pre-commit (already installed)"
    else
        echo "  Installing pre-commit..."
        pipx install pre-commit 2>/dev/null || pip install --user pre-commit
        echo -e "  ${GREEN}pre-commit installed${NC}"
    fi

    # yq (YAML processor — binary release)
    if installed yq; then
        echo -e "  ${GREEN}skip${NC}  yq (already installed)"
    else
        echo "  Installing yq..."
        sudo wget -qO /usr/local/bin/yq \
            https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
        sudo chmod +x /usr/local/bin/yq
        echo -e "  ${GREEN}yq installed${NC}"
    fi

    echo ""
fi

# ── Done ────────────────────────────────────────────────────────────
echo -e "${BOLD}${GREEN}CLI tools installation complete.${NC}"
echo ""
echo "Next steps:"
echo "  1. Restart your shell (or: source ~/.zshrc)"
echo "  2. Run: install-cli-tools.sh --check"
echo "  3. Run: distro-health-check --category cli-tools"
