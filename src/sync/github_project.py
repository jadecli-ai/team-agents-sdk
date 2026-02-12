"""Sync tasks to GitHub Issues + Projects v2 via gh CLI."""

from __future__ import annotations

import asyncio
import json
import logging
from uuid import UUID

import sqlalchemy as sa

from src.db.engine import get_session_factory
from src.db.tables import tasks, subtasks
from src.get_env import env
from src.models.enums import SubtaskType, TaskStatus

logger = logging.getLogger(__name__)

# Map TaskStatus → GitHub Project status field value
_STATUS_MAP = {
    TaskStatus.pending: "Todo",
    TaskStatus.in_progress: "In Progress",
    TaskStatus.blocked: "Blocked",
    TaskStatus.completed: "Done",
    TaskStatus.failed: "Failed",
    TaskStatus.cancelled: "Cancelled",
}


async def _run_gh(*args: str) -> str:
    """Run a gh CLI command and return stdout."""
    proc = await asyncio.create_subprocess_exec(
        "gh", *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {stderr.decode().strip()}")
    return stdout.decode().strip()


async def sync_task_to_github(task_id: UUID) -> dict:
    """Create or update a GitHub issue and project item for a task.

    Returns dict with github_issue_number and github_project_item_id.
    """
    repo = env("PRJ_GITHUB_REPO")
    project_num = int(env("PRJ_GITHUB_PROJECT_NUMBER"))

    session_factory = get_session_factory()
    async with session_factory() as session:
        row = (
            await session.execute(
                sa.select(tasks).where(tasks.c.id == task_id)
            )
        ).mappings().first()
        if row is None:
            raise ValueError(f"Task {task_id} not found")

    title = row["title"]
    description = row["description"] or ""
    status = row["status"]
    issue_number = row["github_issue_number"]
    project_item_id = row["github_project_item_id"]

    # Create or update issue
    if issue_number is None:
        result = await _run_gh(
            "issue", "create",
            "--repo", repo,
            "--title", title,
            "--body", description,
            "--json", "number",
        )
        issue_number = json.loads(result)["number"]
        logger.info("Created issue #%d for task %s", issue_number, task_id)
    else:
        await _run_gh(
            "issue", "edit", str(issue_number),
            "--repo", repo,
            "--title", title,
            "--body", description,
        )

    # Add to project if not already
    if project_item_id is None:
        result = await _run_gh(
            "project", "item-add", str(project_num),
            "--owner", repo.split("/")[0],
            "--url", f"https://github.com/{repo}/issues/{issue_number}",
            "--format", "json",
        )
        project_item_id = json.loads(result).get("id")

    # Update project item status
    gh_status = _STATUS_MAP.get(status, "Todo")
    if project_item_id:
        try:
            await _run_gh(
                "project", "item-edit",
                "--project-id", str(project_num),
                "--id", project_item_id,
                "--field-id", "Status",
                "--text", gh_status,
            )
        except RuntimeError:
            logger.warning("Could not update project status for item %s", project_item_id)

    # Persist back to DB
    async with session_factory() as session:
        await session.execute(
            sa.update(tasks)
            .where(tasks.c.id == task_id)
            .values(
                github_issue_number=issue_number,
                github_project_item_id=project_item_id,
            )
        )
        # Create a git_hook subtask to record this sync
        await session.execute(
            sa.insert(subtasks).values(
                parent_task_id=task_id,
                subtask_type=SubtaskType.git_hook,
                title=f"GitHub sync: issue #{issue_number}",
                status=TaskStatus.completed,
                output_summary=f"Synced to {repo}#{issue_number}, project item {project_item_id}",
            )
        )
        await session.commit()

    return {
        "github_issue_number": issue_number,
        "github_project_item_id": project_item_id,
    }
