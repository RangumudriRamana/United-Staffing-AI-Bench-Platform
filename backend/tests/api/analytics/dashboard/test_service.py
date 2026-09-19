from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.analytics.dashboard.service import RecruiterDashboardService
from app.analytics.dashboard.schemas import (
    DashboardTimelineEvent,
    FollowUpItem,
)
from app.analytics.schemas import RecruiterKPIMetrics
from app.analytics.enums import BusinessEventType


def make_service():
    db = MagicMock()
    db.execute = AsyncMock()

    service = RecruiterDashboardService(db)

    return service, db


def make_kpis(recruiter_id=99):
    return RecruiterKPIMetrics(
        recruiter_id=recruiter_id,
        active_consultants=12,
        total_submissions=20,
        interviews_scheduled=8,
        placements_secured=3,
        placement_conversion_rate=15.0,
    )


def make_event(
    *,
    event_type="SUBMISSION_CREATED",
    aggregate_id=123,
    actor_id=99,
    occurred_at=None,
):
    return SimpleNamespace(
        event_type=event_type,
        aggregate_id=aggregate_id,
        actor_id=actor_id,
        occurred_at=occurred_at or datetime(2026, 9, 18, 10, 30),
    )


def make_result(events):
    result = MagicMock()
    result.scalars.return_value.all.return_value = events
    return result


# ---------------------------------------------------------------------------
# build_recruiter_dashboard
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_recruiter_dashboard_composes_all_widgets():
    service, _ = make_service()

    kpis = make_kpis()

    timeline = [
        DashboardTimelineEvent(
            event_type="SUBMISSION_CREATED",
            summary="Test timeline event",
            occurred_at=datetime(2026, 9, 18, 10, 0),
            actor_id=99,
        ),
    ]

    followups = [
        FollowUpItem(
            task_type="ROUTINE_CHECK",
            description="Test follow-up",
            severity="LOW",
        ),
    ]

    service.metrics_service.compute_recruiter_kpis = AsyncMock(
        return_value=kpis
    )
    service.get_recent_activity_timeline = AsyncMock(
        return_value=timeline
    )
    service.generate_actionable_followups = AsyncMock(
        return_value=followups
    )

    result = await service.build_recruiter_dashboard(
        recruiter_id=99
    )

    assert result.summary == kpis
    assert result.timeline == timeline
    assert result.followups == followups

    service.metrics_service.compute_recruiter_kpis.assert_awaited_once_with(99)
    service.get_recent_activity_timeline.assert_awaited_once_with(99)
    service.generate_actionable_followups.assert_awaited_once_with(99)


# ---------------------------------------------------------------------------
# get_recent_activity_timeline
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_recent_activity_timeline_projects_events():
    service, db = make_service()

    occurred_at = datetime(2026, 9, 18, 14, 0)

    events = [
        make_event(
            event_type="SUBMISSION_CREATED",
            aggregate_id=501,
            actor_id=99,
            occurred_at=occurred_at,
        ),
        make_event(
            event_type="PLACEMENT_CREATED",
            aggregate_id=777,
            actor_id=99,
            occurred_at=datetime(2026, 9, 18, 13, 0),
        ),
    ]

    db.execute.return_value = make_result(events)

    result = await service.get_recent_activity_timeline(
        recruiter_id=99
    )

    assert len(result) == 2

    assert result[0].event_type == "SUBMISSION_CREATED"
    assert result[0].summary == (
        "Event type registration recorded automatically "
        "for context ID: 501"
    )
    assert result[0].occurred_at == occurred_at
    assert result[0].actor_id == 99

    assert result[1].event_type == "PLACEMENT_CREATED"
    assert result[1].actor_id == 99

    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_recent_activity_timeline_empty():
    service, db = make_service()

    db.execute.return_value = make_result([])

    result = await service.get_recent_activity_timeline(
        recruiter_id=99,
        limit=5,
    )

    assert result == []
    db.execute.assert_awaited_once()


# ---------------------------------------------------------------------------
# generate_actionable_followups
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_actionable_followups_detects_stalled_submissions():
    service, db = make_service()

    old_event = make_event(
        event_type=BusinessEventType.SUBMISSION_CREATED.value,
        aggregate_id=501,
        actor_id=99,
        occurred_at=datetime.utcnow() - timedelta(days=7),
    )

    db.execute.return_value = make_result([old_event])

    result = await service.generate_actionable_followups(
        recruiter_id=99
    )

    assert len(result) == 1

    item = result[0]

    assert item.task_type == "STALLED_SUBMISSION"
    assert item.severity == "HIGH"
    assert item.target_public_id == "501"
    assert item.description == (
        "Submission tracking index 501 has spent over 5 days "
        "awaiting client feedback review."
    )

    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_actionable_followups_returns_routine_check_when_empty():
    service, db = make_service()

    db.execute.return_value = make_result([])

    result = await service.generate_actionable_followups(
        recruiter_id=99
    )

    assert len(result) == 1

    item = result[0]

    assert item.task_type == "ROUTINE_CHECK"
    assert item.severity == "LOW"
    assert item.target_public_id is None
    assert item.description == (
        "All tracked opportunities show active movement. "
        "Review new incoming requirements for potential matches."
    )


@pytest.mark.asyncio
async def test_generate_actionable_followups_handles_multiple_stalled_submissions():
    service, db = make_service()

    old_events = [
        make_event(
            event_type=BusinessEventType.SUBMISSION_CREATED.value,
            aggregate_id=100 + index,
            actor_id=99,
            occurred_at=datetime.utcnow() - timedelta(days=6 + index),
        )
        for index in range(3)
    ]

    db.execute.return_value = make_result(old_events)

    result = await service.generate_actionable_followups(
        recruiter_id=99
    )

    assert len(result) == 3
    assert all(
        item.task_type == "STALLED_SUBMISSION"
        for item in result
    )
    assert all(
        item.severity == "HIGH"
        for item in result
    )
    assert [
        item.target_public_id for item in result
    ] == ["100", "101", "102"]


@pytest.mark.asyncio
async def test_generate_actionable_followups_preserves_event_target_id():
    service, db = make_service()

    event = make_event(
        event_type=BusinessEventType.SUBMISSION_CREATED.value,
        aggregate_id=98765,
        actor_id=99,
        occurred_at=datetime.utcnow() - timedelta(days=10),
    )

    db.execute.return_value = make_result([event])

    result = await service.generate_actionable_followups(
        recruiter_id=99
    )

    assert result[0].target_public_id == "98765"