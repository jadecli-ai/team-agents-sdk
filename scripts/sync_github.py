"""CLI entry: sync all pending/in-progress tasks to GitHub."""

from __future__ import annotations

import asyncio
import sqlalchemy as sa

from src.db.engine import get_session_factory, dispose_engine
from src.db.tables import tasks
from src.sync.github_project import sync_task_to_github


async def main():
    factory = get_session_factory()

    async with factory() as session:
        rows = (
            (
                await session.execute(
                    sa.select(tasks.c.id, tasks.c.title, tasks.c.status).where(
                        tasks.c.status.in_(["pending", "in_progress", "blocked"])
                    )
                )
            )
            .mappings()
            .all()
        )

    print(f"Found {len(rows)} tasks to sync")

    for row in rows:
        print(f"  Syncing: {row['title']} ({row['status']})")
        try:
            result = await sync_task_to_github(row["id"])
            print(f"    → issue #{result['github_issue_number']}")
        except Exception as e:
            print(f"    → FAILED: {e}")

    await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
