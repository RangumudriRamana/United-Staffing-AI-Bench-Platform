from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from app.core.exceptions import AppException
from app.tasks.enums import TaskPriority, TaskStatus, TaskType
from app.tasks.service import TaskService


def make_service():
    db = MagicMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()

    service = TaskService(db)

    return service, db


def make_payload():
    return SimpleNamespace(
        owner_id=99,
        task_type=TaskType.FOLLOW_UP_CONSULTANT,
        priority=TaskPriority.NORMAL,
        title="Follow up with consultant",
        description="Contact consultant for availability.",
        related_entity_type="CONSULTANT",
        related_entity_id=123,
        due_at=datetime(2026, 9, 20, 10, 0),
    )


def make_task(
    *,
    owner_id=99,
    status=TaskStatus.OPEN,
    public_id=None,
):
    return SimpleNamespace(
        public_id=public_id
        or UUID("11111111-1111-1111-1111-111111111111"),
        owner_id=owner_id,
        status=status,
        completed_at=None,
    )


def make_result(task):
    result = MagicMock()
    result.scalars.return_value.first.return_value = task
    return result


def make_list_result(tasks):
    result = MagicMock()
    result.scalars.return_value.all.return_value = tasks
    return result


# ---------------------------------------------------------------------------
# create_operational_task
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_operational_task_success():
    service, db = make_service()

    payload = make_payload()

    result = await service.create_operational_task(payload)

    db.add.assert_called_once()

    created_task = db.add.call_args.args[0]

    assert created_task.owner_id == payload.owner_id
    assert created_task.task_type == payload.task_type
    assert created_task.priority == payload.priority
    assert created_task.title == payload.title
    assert created_task.description == payload.description
    assert created_task.related_entity_type == payload.related_entity_type
    assert created_task.related_entity_id == payload.related_entity_id
    assert created_task.due_at == payload.due_at
    assert created_task.status == TaskStatus.OPEN

    db.commit.assert_awaited_once()
    assert result is created_task


# ---------------------------------------------------------------------------
# complete_target_task
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_complete_target_task_not_found():
    service, db = make_service()

    db.execute.return_value = make_result(None)

    public_id = UUID("11111111-1111-1111-1111-111111111111")

    with pytest.raises(AppException) as exc:
        await service.complete_target_task(
            public_id=public_id,
            current_user_id=99,
        )

    assert exc.value.status_code == 404
    assert exc.value.message == "Target action item record not found."
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_complete_target_task_wrong_owner():
    service, db = make_service()

    task = make_task(owner_id=100)

    db.execute.return_value = make_result(task)

    with pytest.raises(AppException) as exc:
        await service.complete_target_task(
            public_id=task.public_id,
            current_user_id=99,
        )

    assert exc.value.status_code == 403
    assert exc.value.message == "Unauthorized interaction context boundary."
    assert task.status == TaskStatus.OPEN
    assert task.completed_at is None
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_complete_target_task_already_completed_returns_unchanged():
    service, db = make_service()

    completed_at = datetime(2026, 9, 18, 12, 0)

    task = make_task(
        owner_id=99,
        status=TaskStatus.COMPLETED,
    )
    task.completed_at = completed_at

    db.execute.return_value = make_result(task)

    result = await service.complete_target_task(
        public_id=task.public_id,
        current_user_id=99,
    )

    assert result is task
    assert task.status == TaskStatus.COMPLETED
    assert task.completed_at == completed_at
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_complete_target_task_success():
    service, db = make_service()

    task = make_task(
        owner_id=99,
        status=TaskStatus.IN_PROGRESS,
    )

    db.execute.return_value = make_result(task)

    result = await service.complete_target_task(
        public_id=task.public_id,
        current_user_id=99,
    )

    assert result is task
    assert task.status == TaskStatus.COMPLETED
    assert task.completed_at is not None
    assert task.completed_at.tzinfo is None

    db.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# fetch_user_active_queue
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_user_active_queue_returns_tasks():
    service, db = make_service()

    task_1 = make_task()
    task_2 = make_task(
        public_id=UUID("22222222-2222-2222-2222-222222222222"),
        status=TaskStatus.IN_PROGRESS,
    )

    db.execute.return_value = make_list_result(
        [task_1, task_2]
    )

    result = await service.fetch_user_active_queue(
        user_id=99,
    )

    assert result == [task_1, task_2]
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_user_active_queue_empty():
    service, db = make_service()

    db.execute.return_value = make_list_result([])

    result = await service.fetch_user_active_queue(
        user_id=99,
    )

    assert result == []
    db.execute.assert_awaited_once()