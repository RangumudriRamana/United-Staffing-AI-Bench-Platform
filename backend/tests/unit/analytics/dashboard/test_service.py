from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.analytics.dashboard.schemas import (
    RecruiterKPIMetrics,
    FollowUpItem,
    DashboardTimelineEvent,
)
from app.analytics.dashboard.service import RecruiterDashboardService
from app.analytics.enums import BusinessEventType


def make_service():
    db = MagicMock()
    service = RecruiterDashboardService(db)
    service.metrics_service = MagicMock()
    return service, db


@pytest.mark.asyncio
async def test_build_recruiter_dashboard_composes_widgets():
    service, _ = make_service()

    kpi_summary = RecruiterKPIMetrics(
        recruiter_id=123,
        active_consultants=5,
        total_submissions=10,
        interviews_scheduled=3,
        placements_secured=2,
        placement_conversion_rate=20.0,
    )

    timeline = [
        DashboardTimelineEvent(
            event_type="SUBMISSION_CREATED",
            summary="Test event",
            occurred_at=datetime(2026, 9, 18, 10, 30),
            actor_id=123,
        )
    ]

    followups = [
        FollowUpItem(
            task_type="ROUTINE_CHECK",
            description="Test follow-up",
            severity="LOW",
        )
    ]

    service.metrics_service.compute_recruiter_kpis = AsyncMock(
        return_value=kpi_summary
    )
    service.get_recent_activity_timeline = AsyncMock(
        return_value=timeline
    )
    service.generate_actionable_followups = AsyncMock(
        return_value=followups
    )

    result = await service.build_recruiter_dashboard(recruiter_id=123)

    assert result.summary == kpi_summary
    assert result.followups == followups
    assert result.timeline == timeline

    service.metrics_service.compute_recruiter_kpis.assert_awaited_once_with(123)
    service.get_recent_activity_timeline.assert_awaited_once_with(123)
    service.generate_actionable_followups.assert_awaited_once_with(123)


@pytest.mark.asyncio
async def test_get_recent_activity_timeline_maps_events():
    service, db = make_service()

    occurred_at = datetime(2026, 9, 18, 10, 30)

    event = SimpleNamespace(
        event_type="SUBMISSION_CREATED",
        aggregate_id="abc-123",
        occurred_at=occurred_at,
        actor_id=123,
    )

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [event]
    db.execute = AsyncMock(return_value=result_mock)

    result = await service.get_recent_activity_timeline(
        recruiter_id=123,
        limit=10,
    )

    assert len(result) == 1
    assert result[0].event_type == "SUBMISSION_CREATED"
    assert "abc-123" in result[0].summary
    assert result[0].occurred_at == occurred_at
    assert result[0].actor_id == 123

    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_recent_activity_timeline_returns_empty_list():
    service, db = make_service()

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=result_mock)

    result = await service.get_recent_activity_timeline(recruiter_id=123)

    assert result == []


@pytest.mark.asyncio
async def test_generate_actionable_followups_creates_stalled_submission_items():
    service, db = make_service()

    old_event = SimpleNamespace(
        aggregate_id="submission-123",
    )

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [old_event]
    db.execute = AsyncMock(return_value=result_mock)

    result = await service.generate_actionable_followups(recruiter_id=123)

    assert len(result) == 1
    assert result[0].task_type == "STALLED_SUBMISSION"
    assert result[0].severity == "HIGH"
    assert result[0].target_public_id == "submission-123"
    assert "submission-123" in result[0].description

    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_actionable_followups_returns_routine_check_when_empty():
    service, db = make_service()

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=result_mock)

    result = await service.generate_actionable_followups(recruiter_id=123)

    assert len(result) == 1
    assert result[0].task_type == "ROUTINE_CHECK"
    assert result[0].severity == "LOW"
    assert result[0].target_public_id is None


@pytest.mark.asyncio
async def test_generate_actionable_followups_maps_multiple_stalled_submissions():
    service, db = make_service()

    events = [
        SimpleNamespace(aggregate_id="submission-1"),
        SimpleNamespace(aggregate_id="submission-2"),
    ]

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = events
    db.execute = AsyncMock(return_value=result_mock)

    result = await service.generate_actionable_followups(recruiter_id=123)

    assert len(result) == 2
    assert [item.task_type for item in result] == [
        "STALLED_SUBMISSION",
        "STALLED_SUBMISSION",
    ]
    assert [item.target_public_id for item in result] == [
        "submission-1",
        "submission-2",
    ]