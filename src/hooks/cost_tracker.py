"""Cost tracking hook: atomically updates task.actual_cost_usd from SDK ResultMessage."""

from __future__ import annotations

import logging
from uuid import UUID

from src.db.crud import Crud
from src.db.tables import tasks

logger = logging.getLogger(__name__)

_task_crud = Crud(tasks)


async def update_task_cost_from_result(task_id: UUID, result_message) -> None:
    """Atomically add result_message cost to tasks.actual_cost_usd.

    Args:
        task_id: The task to update.
        result_message: A claude_agent_sdk.ResultMessage (or any object with
            a `total_cost_usd` float attribute).
    """
    cost = getattr(result_message, "total_cost_usd", None)
    if cost is None or cost <= 0:
        return

    try:
        await _task_crud.increment(task_id, "actual_cost_usd", cost)
    except Exception:
        logger.exception("Failed to update task cost for task_id=%s", task_id)
