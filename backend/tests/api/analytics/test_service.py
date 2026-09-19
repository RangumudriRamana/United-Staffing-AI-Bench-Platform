from unittest.mock import AsyncMock, MagicMock

import pytest

from app.analytics.enums import BusinessEventType
from app.analytics.service import MetricsEngineService


def make_scalar_result(value):
    result = MagicMock()
    result.scalar.return_value = value
    return result


def make_service():
    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.add = MagicMock()

    service = MetricsEngineService(db)

    return service, db


@pytest.mark.asyncio
async def test_log_domain_event_creates_and_flushes_event():
    service, db = make_service()

    result = await service.log_domain_event(
        event_type=BusinessEventType.SUBMISSION_CREATED,
        aggregate_type="SUBMISSION",
        aggregate_id=101,
        actor_id=7,
    )

    db.add.assert_called_once()
    db.flush.assert_awaited_once()

    event = db.add.call_args.args[0]

    assert event.event_type == BusinessEventType.SUBMISSION_CREATED.value
    assert event.aggregate_type == "SUBMISSION"
    assert event.aggregate_id == 101
    assert event.actor_id == 7
    assert event.metadata_json is None
    assert result is event


@pytest.mark.asyncio
async def test_log_domain_event_preserves_metadata():
    service, db = make_service()

    metadata = {
        "source": "submission_service",
        "operation": "create",
    }

    result = await service.log_domain_event(
        event_type=BusinessEventType.PLACEMENT_CREATED,
        aggregate_type="SUBMISSION",
        aggregate_id=202,
        actor_id=11,
        metadata=metadata,
    )

    event = db.add.call_args.args[0]

    assert event.event_type == BusinessEventType.PLACEMENT_CREATED.value
    assert event.metadata_json == metadata
    assert result is event


@pytest.mark.asyncio
async def test_compute_recruiter_kpis_with_submissions():
    service, db = make_service()

    db.execute.side_effect = [
        make_scalar_result(10),
        make_scalar_result(3),
    ]

    result = await service.compute_recruiter_kpis(
        recruiter_id=25
    )

    assert result.recruiter_id == 25
    assert result.total_submissions == 10
    assert result.placements_secured == 3
    assert result.placement_conversion_rate == 30.0


@pytest.mark.asyncio
async def test_compute_recruiter_kpis_zero_submissions():
    service, db = make_service()

    db.execute.side_effect = [
        make_scalar_result(0),
        make_scalar_result(0),
    ]

    result = await service.compute_recruiter_kpis(
        recruiter_id=25
    )

    assert result.recruiter_id == 25
    assert result.total_submissions == 0
    assert result.placements_secured == 0
    assert result.placement_conversion_rate == 0.0


@pytest.mark.asyncio
async def test_compute_recruiter_kpis_zero_scalar_values():
    service, db = make_service()

    db.execute.side_effect = [
        make_scalar_result(None),
        make_scalar_result(None),
    ]

    result = await service.compute_recruiter_kpis(
        recruiter_id=30
    )

    assert result.total_submissions == 0
    assert result.placements_secured == 0
    assert result.placement_conversion_rate == 0.0


@pytest.mark.asyncio
async def test_compute_recruiter_kpis_rounds_conversion_rate():
    service, db = make_service()

    db.execute.side_effect = [
        make_scalar_result(6),
        make_scalar_result(1),
    ]

    result = await service.compute_recruiter_kpis(
        recruiter_id=31
    )

    assert result.total_submissions == 6
    assert result.placements_secured == 1
    assert result.placement_conversion_rate == 16.67