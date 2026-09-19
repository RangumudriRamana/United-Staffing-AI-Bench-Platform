from datetime import datetime

import pytest

from app.models.user import User
from app.tasks.enums import TaskPriority, TaskStatus, TaskType
from app.tasks.models import Task


@pytest.mark.api
@pytest.mark.asyncio
async def test_list_my_tasks(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    task = Task(
        owner_id=sample_admin.id,
        task_type=TaskType.FOLLOW_UP_VENDOR,
        priority=TaskPriority.NORMAL,
        status=TaskStatus.OPEN,
        title="Test vendor follow-up",
        description="Follow up with vendor recruiter.",
        related_entity_type="CONSULTANT",
        related_entity_id=None,
        due_at=datetime.utcnow(),
    )

    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    response = await client.get(
        "/api/v1/tasks/my",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["public_id"] == str(task.public_id)
    assert data[0]["owner_id"] == sample_admin.id
    assert data[0]["task_type"] == "FOLLOW_UP_VENDOR"
    assert data[0]["priority"] == "NORMAL"
    assert data[0]["status"] == "OPEN"
    assert data[0]["title"] == "Test vendor follow-up"


@pytest.mark.api
@pytest.mark.asyncio
async def test_complete_my_task(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    task = Task(
        owner_id=sample_admin.id,
        task_type=TaskType.FOLLOW_UP_VENDOR,
        priority=TaskPriority.NORMAL,
        status=TaskStatus.OPEN,
        title="Test task completion",
        description="Task completion regression test.",
        related_entity_type="CONSULTANT",
        related_entity_id=None,
        due_at=datetime.utcnow(),
    )

    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    response = await client.post(
        f"/api/v1/tasks/{task.public_id}/complete",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["public_id"] == str(task.public_id)
    assert data["owner_id"] == sample_admin.id
    assert data["status"] == "COMPLETED"
    assert data["completed_at"] is not None

    await db_session.refresh(task)

    assert task.status == TaskStatus.COMPLETED
    assert task.completed_at is not None