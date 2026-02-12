# /sync $ARGUMENTS

Sync tasks to GitHub Issues + Projects v2.

## Context
- Read `src/sync/github_project.py` for the sync implementation
- Read `scripts/sync_github.py` for the CLI entry point

## Steps
1. Run `make sync-github` (syncs all pending tasks)
2. Report: issues created/updated, project items added, any errors

If $ARGUMENTS is a UUID: sync only that task via `sync_task_to_github(uuid)`.
If $ARGUMENTS is "all": run the full sync script.
