from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.planner.service import PlannerService
from app.tasks.enums import TaskPriority, TaskStatus, TaskType


def make_service():
    db = MagicMock()
    db.execute = AsyncMock()

    service = PlannerService(db)

    return service, db


def make_task(
    *,
    public_id="11111111-1111-1111-1111-111111111111",
    title="Test Task",
    task_type=TaskType.FOLLOW_UP_CONSULTANT,
    priority=TaskPriority.NORMAL,
    status=TaskStatus.OPEN,
    due_at=None,
):
    return SimpleNamespace(
        public_id=public_id,
        title=title,
        task_type=task_type,
        priority=priority,
        status=status,
        due_at=due_at or datetime(2026, 9, 18, 10, 0),
    )


def make_result(tasks):
    result = MagicMock()
    result.scalars.return_value.all.return_value = tasks
    return result


# ---------------------------------------------------------------------------
# Empty planner
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_daily_plan_empty():
    service, db = make_service()

    planner_date = date(2026, 9, 18)
    db.execute.return_value = make_result([])

    result = await service.get_daily_plan(
        user_id=99,
        planner_date=planner_date,
    )

    assert result["summary"]["planner_date"] == planner_date
    assert result["summary"]["open_tasks"] == 0
    assert result["summary"]["urgent_tasks"] == 0
    assert result["summary"]["high_priority_tasks"] == 0
    assert result["summary"]["marketing_follow_ups"] == 0
    assert result["summary"]["submission_follow_ups"] == 0
    assert result["summary"]["vendor_outreach"] == 0
    assert result["tasks"] == []

    db.execute.assert_awaited_once()


# ---------------------------------------------------------------------------
# Priority classification
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_daily_plan_counts_urgent_and_high_priority_tasks():
    service, db = make_service()

    planner_date = date(2026, 9, 18)

    tasks = [
        make_task(
            title="Urgent 1",
            priority=TaskPriority.URGENT,
        ),
        make_task(
            title="Urgent 2",
            priority=TaskPriority.URGENT,
        ),
        make_task(
            title="High 1",
            priority=TaskPriority.HIGH,
        ),
        make_task(
            title="Normal",
            priority=TaskPriority.NORMAL,
        ),
    ]

    db.execute.return_value = make_result(tasks)

    result = await service.get_daily_plan(
        user_id=99,
        planner_date=planner_date,
    )

    assert result["summary"]["open_tasks"] == 4
    assert result["summary"]["urgent_tasks"] == 2
    assert result["summary"]["high_priority_tasks"] == 1


# ---------------------------------------------------------------------------
# Marketing / submission / vendor categorization
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_daily_plan_counts_marketing_follow_ups():
    service, db = make_service()

    planner_date = date(2026, 9, 18)

    tasks = [
        make_task(task_type=TaskType.FOLLOW_UP_CONSULTANT),
        make_task(task_type=TaskType.MARKETING_REFRESH),
        make_task(task_type=TaskType.FOLLOW_UP_CONSULTANT),
        make_task(task_type=TaskType.SUBMIT_PROFILE),
    ]

    db.execute.return_value = make_result(tasks)

    result = await service.get_daily_plan(
        user_id=99,
        planner_date=planner_date,
    )

    assert result["summary"]["marketing_follow_ups"] == 3
    assert result["summary"]["submission_follow_ups"] == 1


@pytest.mark.asyncio
async def test_get_daily_plan_counts_submission_follow_ups():
    service, db = make_service()

    planner_date = date(2026, 9, 18)

    submission_types = [
        TaskType.SUBMIT_PROFILE,
        TaskType.REQUEST_FEEDBACK,
        TaskType.INTERVIEW_FOLLOW_UP,
        TaskType.INTERVIEW_PREPARATION,
        TaskType.OFFER_REVIEW,
        TaskType.PLACEMENT_CONFIRMATION,
    ]

    tasks = [
        make_task(task_type=task_type)
        for task_type in submission_types
    ]

    db.execute.return_value = make_result(tasks)

    result = await service.get_daily_plan(
        user_id=99,
        planner_date=planner_date,
    )

    assert result["summary"]["submission_follow_ups"] == 6
    assert result["summary"]["marketing_follow_ups"] == 0
    assert result["summary"]["vendor_outreach"] == 0


@pytest.mark.asyncio
async def test_get_daily_plan_counts_vendor_and_client_outreach():
    service, db = make_service()

    planner_date = date(2026, 9, 18)

    tasks = [
        make_task(task_type=TaskType.FOLLOW_UP_VENDOR),
        make_task(task_type=TaskType.FOLLOW_UP_CLIENT),
        make_task(task_type=TaskType.FOLLOW_UP_VENDOR),
        make_task(task_type=TaskType.REQUEST_FEEDBACK),
    ]

    db.execute.return_value = make_result(tasks)

    result = await service.get_daily_plan(
        user_id=99,
        planner_date=planner_date,
    )

    assert result["summary"]["vendor_outreach"] == 3
    assert result["summary"]["submission_follow_ups"] == 1


# ---------------------------------------------------------------------------
# Task serialization
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_daily_plan_serializes_task_details():
    service, db = make_service()

    planner_date = date(2026, 9, 18)
    due_at = datetime(2026, 9, 18, 14, 30)

    task = make_task(
        public_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        title="Submit consultant profile",
        task_type=TaskType.SUBMIT_PROFILE,
        priority=TaskPriority.HIGH,
        status=TaskStatus.IN_PROGRESS,
        due_at=due_at,
    )

    db.execute.return_value = make_result([task])

    result = await service.get_daily_plan(
        user_id=42,
        planner_date=planner_date,
    )

    assert len(result["tasks"]) == 1

    serialized = result["tasks"][0]

    assert serialized["public_id"] == (
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    )
    assert serialized["title"] == "Submit consultant profile"
    assert serialized["task_type"] == TaskType.SUBMIT_PROFILE.value
    assert serialized["priority"] == TaskPriority.HIGH.value
    assert serialized["status"] == TaskStatus.IN_PROGRESS.value
    assert serialized["due_at"] == due_at


# ---------------------------------------------------------------------------
# Combined planner scenario
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_daily_plan_combines_all_categories():
    service, db = make_service()

    planner_date = date(2026, 9, 18)

    tasks = [
        make_task(
            title="Urgent vendor",
            task_type=TaskType.FOLLOW_UP_VENDOR,
            priority=TaskPriority.URGENT,
        ),
        make_task(
            title="Client outreach",
            task_type=TaskType.FOLLOW_UP_CLIENT,
            priority=TaskPriority.HIGH,
        ),
        make_task(
            title="Marketing refresh",
            task_type=TaskType.MARKETING_REFRESH,
        ),
        make_task(
            title="Interview follow-up",
            task_type=TaskType.INTERVIEW_FOLLOW_UP,
        ),
        make_task(
            title="Offer review",
            task_type=TaskType.OFFER_REVIEW,
        ),
        make_task(
            title="Normal consultant task",
            task_type=TaskType.FOLLOW_UP_CONSULTANT,
        ),
    ]

    db.execute.return_value = make_result(tasks)

    result = await service.get_daily_plan(
        user_id=99,
        planner_date=planner_date,
    )

    summary = result["summary"]

    assert summary["open_tasks"] == 6
    assert summary["urgent_tasks"] == 1
    assert summary["high_priority_tasks"] == 1
    assert summary["marketing_follow_ups"] == 2
    assert summary["submission_follow_ups"] == 2
    assert summary["vendor_outreach"] == 2
    assert len(result["tasks"]) == 6