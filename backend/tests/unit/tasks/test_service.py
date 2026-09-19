from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.exceptions import AppException
from app.tasks.enums import TaskStatus
from app.tasks.service import TaskService


def make_service():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.execute = AsyncMock()
    return db, TaskService(db)


def scalar_result(value):
    result = MagicMock()
    result.scalars.return_value.first.return_value = value
    return result


@pytest.mark.asyncio
async def test_create_operational_task():
    db, service = make_service()

    payload = SimpleNamespace(
        owner_id=10,
        task_type="FOLLOW_UP_VENDOR",
        priority="NORMAL",
        title="Follow up",
        description="Contact vendor",
        related_entity_type="VENDOR",
        related_entity_id=20,
        due_at=datetime(2026, 1, 10, 12, 0),
    )

    result = await service.create_operational_task(payload)

    db.add.assert_called_once()
    db.commit.assert_awaited_once()

    assert result.owner_id == 10
    assert result.task_type == "FOLLOW_UP_VENDOR"
    assert result.priority == "NORMAL"
    assert result.title == "Follow up"
    assert result.description == "Contact vendor"
    assert result.related_entity_type == "VENDOR"
    assert result.related_entity_id == 20
    assert result.due_at == payload.due_at
    assert result.status == TaskStatus.OPEN


@pytest.mark.asyncio
async def test_complete_target_task_success():
    db, service = make_service()

    task = SimpleNamespace(
        public_id=uuid4(),
        owner_id=10,
        status=TaskStatus.OPEN,
        completed_at=None,
    )

    db.execute.return_value = scalar_result(task)

    result = await service.complete_target_task(
        public_id=task.public_id,
        current_user_id=10,
    )

    assert result is task
    assert task.status == TaskStatus.COMPLETED
    assert task.completed_at is not None
    assert task.completed_at.tzinfo is None
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_target_task_not_found():
    db, service = make_service()

    db.execute.return_value = scalar_result(None)

    with pytest.raises(AppException) as exc_info:
        await service.complete_target_task(uuid4(), 10)

    assert exc_info.value.status_code == 404
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_complete_target_task_wrong_owner():
    db, service = make_service()

    task = SimpleNamespace(
        public_id=uuid4(),
        owner_id=99,
        status=TaskStatus.OPEN,
        completed_at=None,
    )

    db.execute.return_value = scalar_result(task)

    with pytest.raises(AppException) as exc_info:
        await service.complete_target_task(
            public_id=task.public_id,
            current_user_id=10,
        )

    assert exc_info.value.status_code == 403
    assert task.status == TaskStatus.OPEN
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_complete_target_task_already_completed():
    db, service = make_service()

    completed_at = datetime(2026, 1, 1, 10, 0)

    task = SimpleNamespace(
        public_id=uuid4(),
        owner_id=10,
        status=TaskStatus.COMPLETED,
        completed_at=completed_at,
    )

    db.execute.return_value = scalar_result(task)

    result = await service.complete_target_task(
        public_id=task.public_id,
        current_user_id=10,
    )

    assert result is task
    assert task.completed_at == completed_at
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_fetch_user_active_queue():
    db, service = make_service()

    tasks = [
        SimpleNamespace(id=1, status=TaskStatus.OPEN),
        SimpleNamespace(id=2, status=TaskStatus.IN_PROGRESS),
    ]

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.all.return_value = tasks
    db.execute.return_value = result_proxy

    result = await service.fetch_user_active_queue(10)

    assert result == tasks
    assert len(result) == 2
    assert all(
        task.status in [TaskStatus.OPEN, TaskStatus.IN_PROGRESS]
        for task in result
    )


@pytest.mark.asyncio
async def test_fetch_user_active_queue_empty():
    db, service = make_service()

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.all.return_value = []
    db.execute.return_value = result_proxy

    result = await service.fetch_user_active_queue(999)

    assert result == []