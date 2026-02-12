# Feature: Deterministic Developer Usage Guides (GDI Index)

> **GDI** = Guide, Developer, Index — monotonically increasing, deterministic,
> path-addressable usage guides for the `jadecli-ai` organization.

## Problem

We have 21 GitHub Issues reference docs in `docs/references/github-issues/` and 10
slash commands in `.claude/commands/` (L0-L9), but no structured bridge between
"GitHub has this feature" and "here's exactly where in our org to configure it and
what to tell Claude Code to implement it."

Developers joining the org (human or agent) must read scattered docs, reverse-engineer
the org layout, and guess which Claude Code prompt to run. This is non-deterministic,
token-expensive, and error-prone.

## Solution

Create `usage-guides/developer/` at the repo root with a monotonically increasing
index of actionable guides. Each guide is a numbered markdown file that provides:

1. **Org-relative path** — where `jadecli-ai/` is root
2. **Navigation** — exact clicks or CLI commands to reach the target
3. **Claude Code prompt** — copy-paste prompt or slash command that implements the feature
4. **Reference** — links back to the source GitHub docs guide

The numbering is dependency-ordered: lower numbers are prerequisites for higher numbers.
GDI-001 must be done before GDI-004. GDI-004 must be done before GDI-006. This mirrors
the L0-L9 slash command philosophy already proven in this repo.

## Guide Index

```
usage-guides/developer/
├── 000-index.md                       # Master table + dependency graph
├── 001-issue-types-setup.md           # Org-level issue type configuration
├── 002-label-taxonomy.md              # Org-wide label standardization
├── 003-issue-templates.md             # Per-repo issue + PR templates
├── 004-project-creation.md            # Create Projects v2 for the org
├── 005-project-custom-fields.md       # Priority, Iteration, Estimate, Date fields
├── 006-project-views.md               # Table, Board, Roadmap configurations
├── 007-sub-issues-hierarchy.md        # Epic → Story → Task → Subtask via sub-issues
├── 008-issue-dependencies.md          # Blocking / blocked-by relationships
├── 009-milestones.md                  # Release-based date tracking
├── 010-built-in-automations.md        # Status workflows (auto-todo, auto-done)
├── 011-project-templates.md           # Org templates (up to 6 recommended)
├── 012-actions-automation.md          # GitHub Actions → Projects v2 integration
├── 013-api-integration.md             # GraphQL API for programmatic management
├── 014-saved-views-dashboard.md       # Personal developer issue dashboards
├── 015-charts-insights.md             # Project analytics and burndown
├── 016-filtering-search.md            # Advanced query syntax + CLI search
└── 017-claude-code-sync-bridge.md     # Bidirectional: Claude Code tasks ↔ GitHub Issues
```

## Dependency Chain

```
GDI-001 Issue Types ──┐
GDI-002 Labels ───────┤
GDI-003 Templates ────┼── GDI-004 Project Creation ──┬── GDI-005 Custom Fields
                      │                               ├── GDI-006 Views
                      │                               ├── GDI-010 Automations
                      │                               ├── GDI-011 Templates
                      │                               └── GDI-015 Charts
                      │
GDI-007 Sub-Issues ───┤
GDI-008 Dependencies ─┤
GDI-009 Milestones ───┘
                          GDI-012 Actions ──┐
                          GDI-013 API ──────┼── GDI-017 Claude Code Sync Bridge
                          GDI-016 Search ───┘
                          GDI-014 Saved Views (standalone)
```

## Guide Format (each file)

Every GDI file follows this exact structure:

```markdown
# GDI-{NNN}: {Title}

> Implements: docs/references/github-issues/{NN}-{source}.md
> Depends on: GDI-{NNN}, GDI-{NNN}
> Depended by: GDI-{NNN}, GDI-{NNN}

## Org Path

    jadecli-ai/{repo}/{path-to-target}

## Navigate

{Step-by-step: how to reach this location in the org, via web UI or CLI}

## Claude Code Prompt

    {Exact natural language or slash command to give Claude Code
     that implements this feature using our existing infrastructure}

## Verification

{How to confirm the feature is correctly configured}

## Reference

- Source: docs/references/github-issues/{NN}-{file}.md
- GitHub Docs: {original URL}
```

## Example: GDI-001

```markdown
# GDI-001: Issue Types Setup

> Implements: docs/references/github-issues/07-managing-issue-types.md
> Depends on: (none — this is the first guide)
> Depended by: GDI-003, GDI-004, GDI-007

## Org Path

    jadecli-ai/ → Settings → Planning → Issue types

## Navigate

1. Go to https://github.com/organizations/jadecli-ai/settings/planning
2. Or: `gh api orgs/jadecli-ai` → Settings → Code, planning, and automation → Planning → Issue types

## Claude Code Prompt

    Configure issue types for the jadecli-ai organization.
    Create these types if they don't exist:

    | Type    | Color  | Description                                    |
    |---------|--------|------------------------------------------------|
    | Epic    | purple | Cross-repo initiative spanning multiple sprints |
    | Story   | blue   | User-facing deliverable within a single sprint  |
    | Task    | green  | Atomic unit of work (1-4 agent-hours)           |
    | Subtask | gray   | Breakdown of a Task for parallel execution      |
    | Bug     | red    | Defect in existing behavior                     |
    | Spike   | orange | Time-boxed research or investigation            |

    Keep the 3 GitHub defaults (task, bug, feature) but add Epic, Story,
    Subtask, and Spike. Use `gh api` GraphQL mutations where possible.

## Verification

    gh api graphql -f query='{ organization(login: "jadecli-ai") {
      issueTypes(first: 25) { nodes { name description color } }
    } }'

    Expected: 7 types returned (3 default + 4 custom)

## Reference

- Source: docs/references/github-issues/07-managing-issue-types.md
- GitHub Docs: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/managing-issue-types-in-an-organization
```

## Example: GDI-004

```markdown
# GDI-004: Project Creation

> Implements: docs/references/github-issues/06-creating-a-project.md
> Depends on: GDI-001, GDI-002, GDI-003
> Depended by: GDI-005, GDI-006, GDI-010, GDI-011, GDI-015

## Org Path

    jadecli-ai/ → Projects → New project

## Navigate

1. Go to https://github.com/orgs/jadecli-ai/projects
2. Click "New project" → "Table" (start from scratch)
3. Or via API: see Claude Code prompt below

## Claude Code Prompt

    Create a GitHub Projects v2 board for jadecli-ai.

    Project name: "jadecli-ai Roadmap"
    Description: "Cross-repo planning for team-agents-sdk and pm"
    Visibility: Public (org members)

    Use the GraphQL API via gh cli:

    1. Get org node ID: gh api graphql -f query='{ organization(login: "jadecli-ai") { id } }'
    2. Create project: gh api graphql -f query='mutation { createProjectV2(input: {
         ownerId: "ORG_ID", title: "jadecli-ai Roadmap"
       }) { projectV2 { id url } } }'
    3. Set description and README via updateProjectV2 mutation
    4. Import existing issues from team-agents-sdk and pm repos

    Reference: docs/references/github-issues/19-api-manage-projects.md

## Verification

    gh api graphql -f query='{ organization(login: "jadecli-ai") {
      projectsV2(first: 5) { nodes { id title url } }
    } }'

    Expected: At least 1 project returned with title "jadecli-ai Roadmap"

## Reference

- Source: docs/references/github-issues/06-creating-a-project.md
- GitHub Docs: https://docs.github.com/en/issues/planning-and-tracking-with-projects/creating-projects/creating-a-project
```

## Example: GDI-017

```markdown
# GDI-017: Claude Code Sync Bridge

> Implements: docs/references/github-issues/19-api-manage-projects.md,
>             docs/references/github-issues/21-automating-with-actions.md
> Depends on: GDI-012, GDI-013, GDI-016
> Depended by: (none — this is the capstone guide)

## Org Path

    jadecli-ai/team-agents-sdk/src/sync/github_project.py
    jadecli-ai/team-agents-sdk/.claude/commands/sync.md

## Navigate

1. The sync module lives at `src/sync/github_project.py`
2. The slash command is `/sync` (L8 in the command hierarchy)
3. The Makefile target is `make sync-github`

## Claude Code Prompt

    Enhance the /sync command to support bidirectional sync between
    Claude Code TaskList and GitHub Issues + Projects v2.

    Current state: /sync pushes tasks → GitHub Issues (one-way)
    Target state:  Bidirectional — also pull GitHub Issue updates back
                   into Claude Code task metadata

    Requirements:
    1. Read src/sync/github_project.py for current implementation
    2. Add pull direction: gh issue list → update local task status
    3. Map GDI issue types to Claude Code task metadata
    4. Preserve idempotency (same item synced twice = no duplicate)
    5. Add `make sync-pull` Makefile target
    6. Write tests per /test convention (TDD red/green/refactor)

## Verification

    make sync-github          # Push direction (existing)
    make sync-pull            # Pull direction (new)
    make test                 # All tests pass

## Reference

- Source: docs/references/github-issues/19-api-manage-projects.md
- Source: docs/references/github-issues/21-automating-with-actions.md
- Slash command: .claude/commands/sync.md
```

## Implementation Details

### File structure

```
jadecli-ai/team-agents-sdk/
├── usage-guides/
│   └── developer/
│       ├── 000-index.md          # Master table: GDI-NNN | Title | Org Path | Depends On | Status
│       ├── 001-issue-types-setup.md
│       ├── 002-label-taxonomy.md
│       ├── ...
│       └── 017-claude-code-sync-bridge.md
├── docs/references/github-issues/
│   ├── 01-quickstart-issues.md   # (already exists — knowledge base)
│   └── ...21 files...
└── .claude/commands/
    └── guide.md                  # NEW: /guide slash command (L-1? or standalone)
```

### The `/guide` slash command

A new Claude Code command that reads and executes any GDI guide:

```markdown
# /guide $ARGUMENTS

Execute a developer usage guide from `usage-guides/developer/`.

Parse $ARGUMENTS as a GDI number (e.g., "001") or keyword (e.g., "issue-types").

## Steps
1. Read `usage-guides/developer/000-index.md` to resolve $ARGUMENTS to a file
2. Read the target guide file
3. Check all `Depends on` guides are completed (status = done in 000-index.md)
4. If dependencies not met: STOP and report which guides must be done first
5. Execute the "Claude Code Prompt" section
6. Run the "Verification" section
7. If verification passes: update 000-index.md status to "done"
8. If verification fails: report what went wrong
```

### Path convention

Every path in a GDI guide is relative to the org root `jadecli-ai/`:

| Org-relative path | Resolves to |
|-------------------|------------|
| `jadecli-ai/` | https://github.com/jadecli-ai (org settings) |
| `jadecli-ai/team-agents-sdk/` | https://github.com/jadecli-ai/team-agents-sdk |
| `jadecli-ai/pm/` | https://github.com/jadecli-ai/pm |
| `jadecli-ai/team-agents-sdk/src/sync/` | Local: `~/projects/jadecli-team-agents-sdk/src/sync/` |
| `jadecli-ai/ → Settings → Planning` | https://github.com/organizations/jadecli-ai/settings/planning |

### Determinism guarantees

1. **Monotonic numbering**: GDI-001 < GDI-002 < ... < GDI-017. No gaps. No reordering.
2. **Dependency-ordered**: A guide never depends on a higher-numbered guide.
3. **Idempotent**: Running `/guide 001` twice produces the same result.
4. **Self-verifying**: Every guide has a Verification section with expected output.
5. **Single source of truth**: `000-index.md` tracks completion status.

## Benefits

### For human developers
- **Zero ambiguity onboarding**: New org member runs `/guide 001` through `/guide 017`
  sequentially and the entire GitHub org is configured. No tribal knowledge needed.
- **Discoverability**: `000-index.md` is a single file showing every GitHub feature
  the org uses, where it's configured, and whether it's set up.
- **Reproducibility**: If the org is recreated (fork, new GitHub org, migration),
  the guides rebuild the entire configuration deterministically.

### For Claude Code agents
- **Reduced token cost**: Instead of reading all 21 reference docs (50K+ tokens),
  an agent reads one GDI guide (~500 tokens) with the exact prompt and path.
- **Dependency safety**: The `/guide` command enforces ordering — an agent can't
  configure project views (GDI-006) before the project exists (GDI-004).
- **Composability**: `/guide 001 && /guide 002 && /guide 003` chains deterministically.
  A team lead agent can orchestrate all 17 guides across parallel sub-agents
  (respecting the dependency graph).

### For the jadecli-ai org
- **Auditable configuration**: Every GitHub feature decision is documented in a
  versioned, committed file with conventional commit history.
- **State-of-the-art adoption**: The 21 reference docs capture GitHub's full feature
  set (sub-issues, dependencies, Projects v2 API, Actions automation). The GDI guides
  ensure we actually use all of them, not just the obvious ones.
- **Bridge to jadecli/tasks spec**: GDI-017 connects Claude Code's TaskList to GitHub
  Issues, which is the core value proposition of the jadecli platform.

## Follow-Up Tasks

### Immediate (this sprint)

- [ ] **Create `usage-guides/developer/000-index.md`** — master table with all 17 guides,
  dependency graph, and status column (pending/done)
- [ ] **Write GDI-001 through GDI-003** — org-level prerequisites (issue types, labels,
  templates). These have no dependencies and can be written in parallel.
- [ ] **Write GDI-004** — project creation. Depends on 001-003. This unlocks the
  largest branch of the dependency graph.
- [ ] **Create `.claude/commands/guide.md`** — the `/guide` slash command that reads
  and executes GDI files with dependency checking

### Next sprint

- [ ] **Write GDI-005 through GDI-011** — project configuration guides (fields, views,
  sub-issues, dependencies, milestones, automations, templates)
- [ ] **Write GDI-012 and GDI-013** — GitHub Actions and API integration guides
- [ ] **Execute GDI-001 through GDI-011** against the live `jadecli-ai` org using
  `/guide` command. Validate each verification step.

### Backlog

- [ ] **Write GDI-014 through GDI-016** — developer dashboard, charts, advanced search
- [ ] **Write GDI-017** — Claude Code sync bridge (capstone). Requires `/sync` command
  enhancement for bidirectional sync.
- [ ] **Add GDI guides to CLAUDE.md** — reference the guide system in the project's
  CLAUDE.md so all agents discover it automatically
- [ ] **Create org-level `/guide` in `.claude-org/`** — promote the command from
  repo-level to org-level so it works across `team-agents-sdk` and `pm`
- [ ] **Integrate with release-please** — GDI guide execution events could generate
  changelog entries (e.g., "chore(org): configure issue types per GDI-001")
