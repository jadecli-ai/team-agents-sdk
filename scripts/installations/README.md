# GitHub App Installations

Scripts to configure, verify, and manage each GitHub App installed on `jadecli-ai`.

| App | Script | Status check |
|-----|--------|-------------|
| Claude | `claude.sh` | Verifies OAuth secrets + workflow |
| Codacy | `codacy.sh` | Enables repo analysis + quality gate |
| CodeRabbit | `coderabbit.sh` | Creates `.coderabbit.yaml` config |
| GitBook | `gitbook.sh` | Links docs/ directory |
| Renovate | `renovate.sh` | Creates `renovate.json` config |
| Snyk | `snyk.sh` | Enables scanning + creates `.snyk` policy |
| Vercel | `vercel.sh` | Links project + pulls env vars |

## Usage

```bash
# Run all installations
make apps-setup

# Run individual app setup
./scripts/installations/claude.sh
./scripts/installations/renovate.sh
```

## Prerequisites

- GitHub CLI authenticated: `gh auth status`
- Org membership: `jadecli-ai`
- Apps installed at: https://github.com/organizations/jadecli-ai/settings/installations
