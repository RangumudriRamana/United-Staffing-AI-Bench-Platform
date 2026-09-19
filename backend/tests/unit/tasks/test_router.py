from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.tasks.router import (
    list_authenticated_user_tasks,
    mark_active_task_completed,
)


@pytest.mark.asyncio
async def test_list_authenticated_user_tasks():
    expected = [
        {"id": 1, "status": "OPEN"},
        {"id": 2, "status": "IN_PROGRESS"},
    ]

    service = SimpleNamespace(
        fetch_user_active_queue=AsyncMock(return_value=expected)
    )
    current_user = SimpleNamespace(id=101)

    result = await list_authenticated_user_tasks(
        current_user=current_user,
        service=service,
        _role=None,
    )

    assert result == expected
    service.fetch_user_active_queue.assert_awaited_once_with(
        user_id=101,
    )


@pytest.mark.asyncio
async def test_list_authenticated_user_tasks_empty():
    service = SimpleNamespace(
        fetch_user_active_queue=AsyncMock(return_value=[])
    )
    current_user = SimpleNamespace(id=101)

    result = await list_authenticated_user_tasks(
        current_user=current_user,
        service=service,
        _role=None,
    )

    assert result == []


@pytest.mark.asyncio
async def test_mark_active_task_completed():
    public_id = uuid4()
    expected = {"id": 1, "status": "COMPLETED"}

    service = SimpleNamespace(
        complete_target_task=AsyncMock(return_value=expected)
    )
    current_user = SimpleNamespace(id=101)

    result = await mark_active_task_completed(
        public_id=public_id,
        current_user=current_user,
        service=service,
        _role=None,
    )

    assert result == expected
    service.complete_target_task.assert_awaited_once_with(
        public_id=public_id,
        current_user_id=101,
    )


@pytest.mark.asyncio
async def test_mark_active_task_completed_propagates_error():
    public_id = uuid4()

    service = SimpleNamespace(
        complete_target_task=AsyncMock(
            side_effect=ValueError("task failure")
        )
    )
    current_user = SimpleNamespace(id=101)

    with pytest.raises(ValueError, match="task failure"):
        await mark_active_task_completed(
            public_id=public_id,
            current_user=current_user,
            service=service,
            _role=None,
        )