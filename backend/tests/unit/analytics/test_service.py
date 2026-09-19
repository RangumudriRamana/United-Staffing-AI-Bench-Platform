from unittest.mock import AsyncMock, MagicMock

import pytest

from app.analytics.enums import BusinessEventType
from app.analytics.models import BusinessEvent
from app.analytics.schemas import RecruiterKPIMetrics
from app.analytics.service import MetricsEngineService


def make_service():
    db = MagicMock()
    db.flush = AsyncMock()
    db.execute = AsyncMock()
    service = MetricsEngineService(db)
    return service, db


@pytest.mark.asyncio
async def test_log_domain_event_creates_and_flushes_event():
    service, db = make_service()

    metadata = {
        "source": "test",
        "status": "created",
    }

    result = await service.log_domain_event(
        event_type=BusinessEventType.SUBMISSION_CREATED,
        aggregate_type="SUBMISSION",
        aggregate_id=123,
        actor_id=456,
        metadata=metadata,
    )

    assert isinstance(result, BusinessEvent)
    assert result.event_type == BusinessEventType.SUBMISSION_CREATED.value
    assert result.aggregate_type == "SUBMISSION"
    assert result.aggregate_id == 123
    assert result.actor_id == 456
    assert result.metadata_json == metadata
    assert result.occurred_at is not None

    db.add.assert_called_once_with(result)
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_log_domain_event_allows_none_metadata():
    service, db = make_service()

    result = await service.log_domain_event(
        event_type=BusinessEventType.PLACEMENT_CREATED,
        aggregate_type="PLACEMENT",
        aggregate_id=789,
        actor_id=456,
    )

    assert result.event_type == BusinessEventType.PLACEMENT_CREATED.value
    assert result.metadata_json is None

    db.add.assert_called_once_with(result)
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_compute_recruiter_kpis_calculates_conversion_rate():
    service, db = make_service()

    submission_result = MagicMock()
    submission_result.scalar.return_value = 20

    placement_result = MagicMock()
    placement_result.scalar.return_value = 5

    db.execute.side_effect = [
        submission_result,
        placement_result,
    ]

    result = await service.compute_recruiter_kpis(recruiter_id=123)

    assert isinstance(result, RecruiterKPIMetrics)
    assert result.recruiter_id == 123
    assert result.total_submissions == 20
    assert result.placements_secured == 5
    assert result.placement_conversion_rate == 25.0

    assert db.execute.await_count == 2


@pytest.mark.asyncio
async def test_compute_recruiter_kpis_returns_zero_for_none_counts():
    service, db = make_service()

    submission_result = MagicMock()
    submission_result.scalar.return_value = None

    placement_result = MagicMock()
    placement_result.scalar.return_value = None

    db.execute.side_effect = [
        submission_result,
        placement_result,
    ]

    result = await service.compute_recruiter_kpis(recruiter_id=123)

    assert result.recruiter_id == 123
    assert result.total_submissions == 0
    assert result.placements_secured == 0
    assert result.placement_conversion_rate == 0.0


@pytest.mark.asyncio
async def test_compute_recruiter_kpis_zero_submissions_has_zero_conversion():
    service, db = make_service()

    submission_result = MagicMock()
    submission_result.scalar.return_value = 0

    placement_result = MagicMock()
    placement_result.scalar.return_value = 3

    db.execute.side_effect = [
        submission_result,
        placement_result,
    ]

    result = await service.compute_recruiter_kpis(recruiter_id=123)

    assert result.total_submissions == 0
    assert result.placements_secured == 3
    assert result.placement_conversion_rate == 0.0


@pytest.mark.asyncio
async def test_compute_recruiter_kpis_rounds_conversion_rate():
    service, db = make_service()

    submission_result = MagicMock()
    submission_result.scalar.return_value = 3

    placement_result = MagicMock()
    placement_result.scalar.return_value = 1

    db.execute.side_effect = [
        submission_result,
        placement_result,
    ]

    result = await service.compute_recruiter_kpis(recruiter_id=123)

    assert result.total_submissions == 3
    assert result.placements_secured == 1
    assert result.placement_conversion_rate == 33.33