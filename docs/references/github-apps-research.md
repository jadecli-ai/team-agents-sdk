# GitHub Marketplace Apps Research

> Fetched: 2026-02-11

## Recommended Apps for jadecli-ai

### Tier 1: Critical Infrastructure

| App | Free? | Purpose |
|-----|-------|---------|
| Vercel | Yes | Auto preview deploys per PR, prod on merge |
| Neon | Yes | DB branch per PR, schema diff comments |
| Dependabot | Yes (built-in) | Dependency vulnerability scanning |

### Tier 2: Code Review & Quality

| App | Free? | Purpose |
|-----|-------|---------|
| CodeRabbit | Yes (OSS) | AI code review, inline fixes, PR summaries |
| Codacy | Yes (OSS) | SAST + code quality for 49 languages |
| SonarCloud | Yes (OSS) | Code quality gates, bug/vuln detection |

### Tier 3: Dependency & Security

| App | Free? | Purpose |
|-----|-------|---------|
| Renovate | Fully free | Auto dependency update PRs (npm + pip) |
| Snyk | Limited free | Dependency + container security |
| Gitleaks | Yes (OSS) | Secret detection in commits |

### Tier 4: Communication & Docs

| App | Free? | Purpose |
|-----|-------|---------|
| Slack-GitHub | Yes | PR/issue/deploy notifications |
| GitBook | Free tier | Auto-sync docs from repo |

## Neon GitHub Actions

| Action | Purpose |
|--------|---------|
| `neondatabase/create-branch-action@v5` | Create DB branch per PR |
| `neondatabase/delete-branch-action@v3` | Delete branch on PR close |
| `neondatabase/schema-diff-action@v1` | Schema diff comment on PR |
| `neondatabase/reset-branch-action` | Reset branch to parent |
| `neondatabase/setup-neon-action` | Install neonctl in CI |
