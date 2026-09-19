from unittest.mock import AsyncMock, MagicMock

import pytest

from app.analytics.executive.service import ExecutiveDashboardService
from app.auth.enums import Role


def make_scalar_result(value):
    result = MagicMock()
    result.scalar.return_value = value
    return result


def make_service():
    db = MagicMock()
    db.execute = AsyncMock()
    service = ExecutiveDashboardService(db)
    return service, db


@pytest.mark.asyncio
async def test_build_executive_dashboard_with_recruiter_data():
    service, db = make_service()

    recruiter = MagicMock()
    recruiter.id = 101
    recruiter.first_name = "John"
    recruiter.last_name = "Smith"

    recruiter_result = MagicMock()
    recruiter_result.scalars.return_value.all.return_value = [recruiter]

    db.execute.side_effect = [
        # total consultants
        make_scalar_result(50),
        # available consultants
        make_scalar_result(20),
        # active requirements
        make_scalar_result(10),
        # submissions
        make_scalar_result(40),
        # placements
        make_scalar_result(8),
        # marketing active
        make_scalar_result(15),
        # placed
        make_scalar_result(5),
        # recruiters
        recruiter_result,
        # recruiter submissions
        make_scalar_result(10),
        # recruiter placements
        make_scalar_result(3),
    ]

    result = await service.build_executive_dashboard()

    assert result.summary.total_consultants == 50
    assert result.summary.available_consultants == 20
    assert result.summary.active_requirements == 10
    assert result.summary.active_submissions == 40
    assert result.summary.placements_this_month == 8

    assert result.bench_health.available == 20
    assert result.bench_health.marketing_active == 15
    assert result.bench_health.placed == 5
    assert result.bench_health.idle_greater_30_days == 5

    assert len(result.recruiter_performance) == 1
    recruiter_metrics = result.recruiter_performance[0]

    assert recruiter_metrics.recruiter_name == "John Smith"
    assert recruiter_metrics.submissions_count == 10
    assert recruiter_metrics.placements_count == 3
    assert recruiter_metrics.conversion_rate == 30.0

    assert result.forecast.expected_placements_this_month == 9
    assert result.forecast.pipeline_growth_velocity == "STABLE"

    assert db.execute.await_count == 10


@pytest.mark.asyncio
async def test_build_executive_dashboard_with_no_recruiters():
    service, db = make_service()

    recruiter_result = MagicMock()
    recruiter_result.scalars.return_value.all.return_value = []

    db.execute.side_effect = [
        make_scalar_result(30),
        make_scalar_result(12),
        make_scalar_result(7),
        make_scalar_result(20),
        make_scalar_result(4),
        make_scalar_result(8),
        make_scalar_result(3),
        recruiter_result,
    ]

    result = await service.build_executive_dashboard()

    assert result.summary.total_consultants == 30
    assert result.summary.available_consultants == 12
    assert result.summary.active_requirements == 7
    assert result.summary.active_submissions == 20
    assert result.summary.placements_this_month == 4

    assert result.bench_health.available == 12
    assert result.bench_health.marketing_active == 8
    assert result.bench_health.placed == 3
    assert result.bench_health.idle_greater_30_days == 4

    assert result.recruiter_performance == []

    assert result.forecast.expected_placements_this_month == 5
    assert result.forecast.pipeline_growth_velocity == "STABLE"

    assert db.execute.await_count == 8


@pytest.mark.asyncio
async def test_build_executive_dashboard_accelerating_pipeline():
    service, db = make_service()

    recruiter_result = MagicMock()
    recruiter_result.scalars.return_value.all.return_value = []

    db.execute.side_effect = [
        make_scalar_result(100),
        make_scalar_result(50),
        make_scalar_result(20),
        make_scalar_result(100),
        make_scalar_result(15),
        make_scalar_result(40),
        make_scalar_result(10),
        recruiter_result,
    ]

    result = await service.build_executive_dashboard()

    assert result.forecast.expected_placements_this_month == 16
    assert result.forecast.pipeline_growth_velocity == "ACCELERATING"


@pytest.mark.asyncio
async def test_build_executive_dashboard_handles_zero_counts():
    service, db = make_service()

    recruiter_result = MagicMock()
    recruiter_result.scalars.return_value.all.return_value = []

    db.execute.side_effect = [
        make_scalar_result(None),
        make_scalar_result(None),
        make_scalar_result(None),
        make_scalar_result(None),
        make_scalar_result(None),
        make_scalar_result(None),
        make_scalar_result(None),
        recruiter_result,
    ]

    result = await service.build_executive_dashboard()

    assert result.summary.total_consultants == 0
    assert result.summary.available_consultants == 0
    assert result.summary.active_requirements == 0
    assert result.summary.active_submissions == 0
    assert result.summary.placements_this_month == 0

    assert result.bench_health.available == 0
    assert result.bench_health.marketing_active == 0
    assert result.bench_health.placed == 0
    assert result.bench_health.idle_greater_30_days == 0

    assert result.recruiter_performance == []

    assert result.forecast.expected_placements_this_month == 1
    assert result.forecast.pipeline_growth_velocity == "STABLE"


@pytest.mark.asyncio
async def test_build_executive_dashboard_recruiter_name_is_trimmed():
    service, db = make_service()

    recruiter = MagicMock()
    recruiter.id = 202
    recruiter.first_name = "Jane"
    recruiter.last_name = ""

    recruiter_result = MagicMock()
    recruiter_result.scalars.return_value.all.return_value = [recruiter]

    db.execute.side_effect = [
        make_scalar_result(10),
        make_scalar_result(5),
        make_scalar_result(2),
        make_scalar_result(5),
        make_scalar_result(1),
        make_scalar_result(3),
        make_scalar_result(1),
        recruiter_result,
        make_scalar_result(5),
        make_scalar_result(1),
    ]

    result = await service.build_executive_dashboard()

    assert result.recruiter_performance[0].recruiter_name == "Jane"
    assert result.recruiter_performance[0].conversion_rate == 20.0