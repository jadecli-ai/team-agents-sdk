"""Reusable async CRUD operations for SQLAlchemy tables.

Usage:
    from src.db.crud import Crud
    from src.db.tables import tasks

    task_crud = Crud(tasks)

    # Create
    row = await task_crud.create(title="Review auth", priority="high")

    # Read
    task = await task_crud.get(some_uuid)
    all_pending = await task_crud.find(status="pending")

    # Update
    await task_crud.update(some_uuid, status="completed", completed_at=now)

    # Delete
    await task_crud.delete(some_uuid)

    # Atomic increment
    await task_crud.increment(some_uuid, "actual_cost_usd", 0.05)
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import Table

from src.db.engine import get_session_factory


class Crud:
    """Generic async CRUD wrapper around a SQLAlchemy Table.

    All methods use the async session factory from engine.py.
    Each method opens and closes its own session (request-scoped).
    """

    def __init__(self, table: Table) -> None:
        self.table = table

    async def create(self, **values: Any) -> dict:
        """Insert a row and return it as a dict."""
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                sa.insert(self.table).values(**values).returning(self.table)
            )
            await session.commit()
            return dict(result.mappings().first())

    async def get(self, id: UUID) -> dict | None:
        """Get a single row by primary key."""
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                sa.select(self.table).where(self.table.c.id == id)
            )
            row = result.mappings().first()
            return dict(row) if row else None

    async def find(self, *, limit: int = 100, order_by: str = "created_at", **filters: Any) -> list[dict]:
        """Find rows matching column filters.

        Args:
            limit: Max rows to return.
            order_by: Column name to sort by (descending). Prefix with "+" for ascending.
            **filters: Column=value equality filters.
        """
        factory = get_session_factory()
        query = sa.select(self.table)

        for col_name, value in filters.items():
            if hasattr(self.table.c, col_name):
                query = query.where(getattr(self.table.c, col_name) == value)

        # Order
        ascending = order_by.startswith("+")
        col_name = order_by.lstrip("+")
        if hasattr(self.table.c, col_name):
            col = getattr(self.table.c, col_name)
            query = query.order_by(col.asc() if ascending else col.desc())

        query = query.limit(limit)

        async with factory() as session:
            result = await session.execute(query)
            return [dict(row) for row in result.mappings().all()]

    async def update(self, id: UUID, **values: Any) -> dict | None:
        """Update a row by primary key and return it."""
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                sa.update(self.table)
                .where(self.table.c.id == id)
                .values(**values)
                .returning(self.table)
            )
            await session.commit()
            row = result.mappings().first()
            return dict(row) if row else None

    async def delete(self, id: UUID) -> bool:
        """Delete a row by primary key. Returns True if deleted."""
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                sa.delete(self.table).where(self.table.c.id == id)
            )
            await session.commit()
            return result.rowcount > 0

    async def increment(self, id: UUID, column: str, amount: float | int) -> dict | None:
        """Atomically increment a numeric column."""
        col = getattr(self.table.c, column)
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                sa.update(self.table)
                .where(self.table.c.id == id)
                .values(**{column: col + amount})
                .returning(self.table)
            )
            await session.commit()
            row = result.mappings().first()
            return dict(row) if row else None

    async def count(self, **filters: Any) -> int:
        """Count rows matching filters."""
        factory = get_session_factory()
        query = sa.select(sa.func.count()).select_from(self.table)
        for col_name, value in filters.items():
            if hasattr(self.table.c, col_name):
                query = query.where(getattr(self.table.c, col_name) == value)

        async with factory() as session:
            result = await session.execute(query)
            return result.scalar() or 0

    async def exists(self, id: UUID) -> bool:
        """Check if a row exists."""
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                sa.select(sa.literal(1)).where(self.table.c.id == id)
            )
            return result.first() is not None
