# WSL2 Distro Full Review Plan

**Distro:** Ubuntu-26.04-jadecli (primary)
**Total size:** 4.9 GB
**Date:** 2026-02-12

## Disk Usage Snapshot

| Directory | Size | Notes |
|-----------|------|-------|
| `.cache/` | 1.4 GB | uv 1.2G, pre-commit 129M, pip 50M |
| `.local/` | 1.3 GB | share 1.1G, bin 230M |
| `.nvm/` | 592 MB | Node version manager |
| `.npm/` | 511 MB | npm cache |
| `.vscode-server/` | 413 MB | VS Code remote extensions |
| `.claude/` | 187 MB | Claude Code config + agents |
| `.npm-global/` | 84 MB | Global npm packages |
| `projects/` | 63 MB | All git repos |
| `.oh-my-zsh/` | 21 MB | Zsh framework |
| Other dotfiles | < 1 MB | ssh, docker, config, etc. |
| `.aws/`, `.azure/` | 0 | Empty placeholder dirs |

## Multi-Agent Review Architecture

```
Team Lead (coordinator)
    |
    ├── Agent 1: security-auditor
    │   Scope: .ssh/, .gnupg/, .aws/, .azure/, .docker/,
    │          .gitconfig, .npmrc, .claude.json, env files
    │   Goal: Find exposed secrets, weak perms, stale credentials
    │
    ├── Agent 2: disk-analyst
    │   Scope: .cache/, .local/, .nvm/, .npm/, .npm-global/,
    │          .vscode-server/, .oh-my-zsh/
    │   Goal: Identify bloat, stale caches, cleanup candidates
    │
    ├── Agent 3: config-reviewer
    │   Scope: .zshrc, .bashrc, .profile, .tmux.conf,
    │          .wezterm.lua, .gitconfig, .config/
    │   Goal: Audit shell/tool configs for consistency and best practices
    │
    ├── Agent 4: claude-infra-reviewer
    │   Scope: .claude/, .claude.json, .claude.json.backup.*,
    │          .claude/agents/, .claude/commands/, .claude/skills/
    │   Goal: Review Claude Code setup, MCP configs, agent definitions,
    │          backup file accumulation
    │
    └── Agent 5: project-structure-reviewer
        Scope: projects/, repos/, bin/,
               26-04-wslg-build-template/
        Goal: Verify repo health, stale clones, PATH scripts,
              template consistency with golden image
```

## Review Categories

### 1. Security Audit (Agent 1)

| Check | Path | What to look for |
|-------|------|------------------|
| SSH keys | `.ssh/` | Key types (ed25519 preferred), permissions (600/700), authorized_keys |
| GPG keys | `.gnupg/` | Keyring state, trust model |
| AWS creds | `.aws/` | credentials file, config regions |
| Azure creds | `.azure/` | Token cache, service principal files |
| Docker auth | `.docker/config.json` | Registry credentials, credential helpers |
| Git config | `.gitconfig` | Signing keys, credential helpers, safe directories |
| npm auth | `.npmrc` | Registry tokens, auth tokens |
| Claude tokens | `.claude.json` | OAuth tokens, API keys, backup accumulation |
| Env files | `*/.env`, `*/neon.env` | Leaked database URLs, API keys |

### 2. Disk & Cache Analysis (Agent 2)

| Check | Path | Expected action |
|-------|------|-----------------|
| uv cache | `.cache/uv/` (1.2 GB) | `uv cache clean` — safe to purge |
| pre-commit cache | `.cache/pre-commit/` (129 MB) | Stale hook envs |
| pip cache | `.cache/pip/` (50 MB) | `pip cache purge` — redundant with uv |
| npm cache | `.npm/` (511 MB) | `npm cache clean --force` |
| nvm versions | `.nvm/versions/` | Which Node versions installed, remove unused |
| npm-global | `.npm-global/` (84 MB) | List global packages, remove unused |
| VS Code server | `.vscode-server/` (413 MB) | Extension count, log files, old versions |
| .local/share | `.local/share/` (1.1 GB) | What's consuming space (mise, uv, etc.) |
| .local/bin | `.local/bin/` (230 MB) | Binary inventory, PATH conflicts |

### 3. Configuration Review (Agent 3)

| Check | File | What to verify |
|-------|------|----------------|
| Zsh config | `.zshrc` | Plugins, theme, PATH entries, aliases |
| Bash config | `.bashrc` | Compatibility with zsh, PATH duplication |
| Profile | `.profile` | Login shell setup, env exports |
| tmux | `.tmux.conf` | Key bindings, pane navigation, mouse mode |
| WezTerm | `.wezterm.lua` | Terminal config, font, color scheme |
| XDG dirs | `.config/` | What tools store configs here |
| Shell completions | `.zcompdump*` | Stale completion caches |

### 4. Claude Infrastructure Review (Agent 4)

| Check | Path | What to verify |
|-------|------|----------------|
| Main config | `.claude.json` | Settings, model preferences, token freshness |
| Backup files | `.claude.json.backup.*` (5 files) | Why so many, safe to delete? |
| MCP servers | `.claude/.mcp.json` | Active servers, correct paths |
| Agents | `.claude/agents/` | Agent definitions, tool access, model assignments |
| Commands | `.claude/commands/` | Slash command definitions |
| Skills | `.claude/skills/` | Skill scripts and configs |
| Plans | `.claude/plans/` | Stale plans from old sessions |
| Research | `.claude/research-results/` | Result freshness, size |
| Settings | `.claude/settings.json` | Permission rules, deny patterns |
| Memory | `.claude/projects/*/memory/` | Memory file accumulation |

### 5. Project Structure Review (Agent 5)

| Check | Path | What to verify |
|-------|------|----------------|
| Primary repos | `projects/jadecli-ai/` | Clone health, branch state, uncommitted changes |
| Secondary repos | `projects/jadecli*/` | Shallow clone status, freshness |
| Stale repos | `repos/` (4 KB) | Empty or abandoned? |
| PATH scripts | `bin/` (8 KB) | What custom scripts, are they in golden image? |
| WSLg template | `26-04-wslg-build-template/` | Purpose, still needed? |
| Golden image alignment | All | Compare current state vs scripts/golden/ expectations |

## Deliverables

Each agent produces a structured findings report:

```json
{
  "agent": "security-auditor",
  "timestamp": "2026-02-12T...",
  "findings": [
    {
      "severity": "critical|high|medium|low|info",
      "category": "credentials|permissions|config|bloat",
      "path": "/home/org-jadecli/.ssh/...",
      "finding": "Description of issue",
      "recommendation": "What to do"
    }
  ],
  "summary": {
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "info": 0
  }
}
```

## Execution Order

1. All 5 agents run in parallel (independent scopes)
2. Team lead collects findings, deduplicates, prioritizes
3. Generate consolidated report at `docs/audits/wsl-distro-findings.json`
4. Create actionable cleanup script at `scripts/golden/distro-audit-fix.sh`
5. Update `scripts/golden/cleanup.sh` with any new cleanup targets discovered

## Golden Image Impact

Findings feed directly into:
- `scripts/golden/cleanup.sh` — new targets for pre-export cleanup
- `scripts/golden/bin/distro-health-check` — new checks if gaps found
- `scripts/golden/install.sh` — config corrections if defaults are wrong
