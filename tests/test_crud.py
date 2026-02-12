"""Tests for the reusable Crud class with mocked sessions."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.db.crud import Crud
from src.db.tables import tasks


@pytest.fixture
def crud():
    return Crud(tasks)


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    return session


class TestCrudCreate:
    @patch("src.db.crud.get_session_factory")
    async def test_create_returns_dict(self, mock_factory, crud, mock_session):
        mock_session.execute.return_value = MagicMock(
            mappings=lambda: MagicMock(
                first=lambda: {"id": uuid4(), "title": "test", "status": "pending"}
            )
        )
        mock_factory.return_value = MagicMock(return_value=mock_session)

        result = await crud.create(title="test", status="pending")
        assert result["title"] == "test"
        mock_session.commit.assert_called_once()


class TestCrudGet:
    @patch("src.db.crud.get_session_factory")
    async def test_get_found(self, mock_factory, crud, mock_session):
        task_id = uuid4()
        mock_session.execute.return_value = MagicMock(
            mappings=lambda: MagicMock(first=lambda: {"id": task_id, "title": "found"})
        )
        mock_factory.return_value = MagicMock(return_value=mock_session)

        result = await crud.get(task_id)
        assert result["title"] == "found"

    @patch("src.db.crud.get_session_factory")
    async def test_get_not_found(self, mock_factory, crud, mock_session):
        mock_session.execute.return_value = MagicMock(
            mappings=lambda: MagicMock(first=lambda: None)
        )
        mock_factory.return_value = MagicMock(return_value=mock_session)

        result = await crud.get(uuid4())
        assert result is None


class TestCrudFind:
    @patch("src.db.crud.get_session_factory")
    async def test_find_with_filters(self, mock_factory, crud, mock_session):
        mock_session.execute.return_value = MagicMock(
            mappings=lambda: MagicMock(
                all=lambda: [
                    {"id": uuid4(), "status": "pending"},
                    {"id": uuid4(), "status": "pending"},
                ]
            )
        )
        mock_factory.return_value = MagicMock(return_value=mock_session)

        results = await crud.find(status="pending")
        assert len(results) == 2


class TestCrudUpdate:
    @patch("src.db.crud.get_session_factory")
    async def test_update_returns_updated(self, mock_factory, crud, mock_session):
        task_id = uuid4()
        mock_session.execute.return_value = MagicMock(
            mappings=lambda: MagicMock(first=lambda: {"id": task_id, "status": "completed"})
        )
        mock_factory.return_value = MagicMock(return_value=mock_session)

        result = await crud.update(task_id, status="completed")
        assert result["status"] == "completed"
        mock_session.commit.assert_called_once()


class TestCrudDelete:
    @patch("src.db.crud.get_session_factory")
    async def test_delete_returns_true(self, mock_factory, crud, mock_session):
        mock_session.execute.return_value = MagicMock(rowcount=1)
        mock_factory.return_value = MagicMock(return_value=mock_session)

        result = await crud.delete(uuid4())
        assert result is True

    @patch("src.db.crud.get_session_factory")
    async def test_delete_not_found_returns_false(self, mock_factory, crud, mock_session):
        mock_session.execute.return_value = MagicMock(rowcount=0)
        mock_factory.return_value = MagicMock(return_value=mock_session)

        result = await crud.delete(uuid4())
        assert result is False


class TestCrudIncrement:
    @patch("src.db.crud.get_session_factory")
    async def test_increment(self, mock_factory, crud, mock_session):
        task_id = uuid4()
        mock_session.execute.return_value = MagicMock(
            mappings=lambda: MagicMock(first=lambda: {"id": task_id, "actual_cost_usd": 0.15})
        )
        mock_factory.return_value = MagicMock(return_value=mock_session)

        result = await crud.increment(task_id, "actual_cost_usd", 0.05)
        assert result is not None
        mock_session.commit.assert_called_once()


class TestCrudCount:
    @patch("src.db.crud.get_session_factory")
    async def test_count(self, mock_factory, crud, mock_session):
        mock_session.execute.return_value = MagicMock(scalar=lambda: 5)
        mock_factory.return_value = MagicMock(return_value=mock_session)

        result = await crud.count(status="pending")
        assert result == 5
