from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.analytics.executive.service import ExecutiveDashboardService


def make_scalar_result(value):
    result = MagicMock()
    result.scalar.return_value = value
    return result


def make_recruiter_result(recruiters):
    result = MagicMock()
    result.scalars.return_value.all.return_value = recruiters
    return result


def make_service():
    db = MagicMock()
    db.execute = AsyncMock()

    service = ExecutiveDashboardService(db)

    return service, db


def make_recruiter(
    recruiter_id=1,
    first_name="John",
    last_name="Doe",
):
    return SimpleNamespace(
        id=recruiter_id,
        first_name=first_name,
        last_name=last_name,
    )


# ---------------------------------------------------------------------------
# build_executive_dashboard - empty/zero data
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_executive_dashboard_with_zero_counts():
    service, db = make_service()

    db.execute.side_effect = [
        make_scalar_result(0),  # total consultants
        make_scalar_result(0),  # available consultants
        make_scalar_result(0),  # active requirements
        make_scalar_result(0),  # submissions
        make_scalar_result(0),  # placements
        make_scalar_result(0),  # marketing active
        make_scalar_result(0),  # placed
        make_recruiter_result([]),  # recruiters
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

    assert db.execute.await_count == 8


# ---------------------------------------------------------------------------
# build_executive_dashboard - normal KPI data
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_executive_dashboard_with_normal_counts():
    service, db = make_service()

    db.execute.side_effect = [
        make_scalar_result(100),  # total consultants
        make_scalar_result(40),   # available consultants
        make_scalar_result(15),   # active requirements
        make_scalar_result(80),   # submissions
        make_scalar_result(12),   # placements
        make_scalar_result(25),   # marketing active
        make_scalar_result(8),    # placed
        make_recruiter_result([]),
    ]

    result = await service.build_executive_dashboard()

    assert result.summary.total_consultants == 100
    assert result.summary.available_consultants == 40
    assert result.summary.active_requirements == 15
    assert result.summary.active_submissions == 80
    assert result.summary.placements_this_month == 12

    assert result.bench_health.available == 40
    assert result.bench_health.marketing_active == 25
    assert result.bench_health.placed == 8

    assert result.bench_health.idle_greater_30_days == 15

    assert result.forecast.expected_placements_this_month == 13
    assert result.forecast.pipeline_growth_velocity == "STABLE"


# ---------------------------------------------------------------------------
# Recruiter performance - zero submissions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_executive_dashboard_recruiter_zero_submissions():
    service, db = make_service()

    recruiter = make_recruiter(
        recruiter_id=10,
        first_name="Alice",
        last_name="Smith",
    )

    db.execute.side_effect = [
        make_scalar_result(20),  # total consultants
        make_scalar_result(10),  # available
        make_scalar_result(5),   # requirements
        make_scalar_result(4),   # submissions
        make_scalar_result(1),   # placements
        make_scalar_result(3),   # marketing active
        make_scalar_result(1),   # placed
        make_recruiter_result([recruiter]),
        make_scalar_result(0),   # recruiter submissions
        make_scalar_result(5),   # recruiter placements
    ]

    result = await service.build_executive_dashboard()

    assert len(result.recruiter_performance) == 1

    performance = result.recruiter_performance[0]

    assert performance.recruiter_name == "Alice Smith"
    assert performance.submissions_count == 0
    assert performance.placements_count == 5
    assert performance.conversion_rate == 0.0


# ---------------------------------------------------------------------------
# Recruiter performance - successful conversion calculation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_executive_dashboard_recruiter_conversion_rate():
    service, db = make_service()

    recruiter = make_recruiter(
        recruiter_id=20,
        first_name="Bob",
        last_name="Jones",
    )

    db.execute.side_effect = [
        make_scalar_result(30),
        make_scalar_result(15),
        make_scalar_result(8),
        make_scalar_result(50),
        make_scalar_result(10),
        make_scalar_result(7),
        make_scalar_result(3),
        make_recruiter_result([recruiter]),
        make_scalar_result(40),  # recruiter submissions
        make_scalar_result(7),   # recruiter placements
    ]

    result = await service.build_executive_dashboard()

    performance = result.recruiter_performance[0]

    assert performance.recruiter_name == "Bob Jones"
    assert performance.submissions_count == 40
    assert performance.placements_count == 7
    assert performance.conversion_rate == 17.5


# ---------------------------------------------------------------------------
# Recruiter name normalization
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_executive_dashboard_recruiter_name_is_stripped():
    service, db = make_service()

    recruiter = make_recruiter(
        recruiter_id=30,
        first_name="  Jane ",
        last_name="  Doe  ",
    )

    db.execute.side_effect = [
        make_scalar_result(10),
        make_scalar_result(5),
        make_scalar_result(2),
        make_scalar_result(20),
        make_scalar_result(3),
        make_scalar_result(4),
        make_scalar_result(2),
        make_recruiter_result([recruiter]),
        make_scalar_result(10),
        make_scalar_result(2),
    ]

    result = await service.build_executive_dashboard()

    assert result.recruiter_performance[0].recruiter_name == "Jane    Doe"


# ---------------------------------------------------------------------------
# Forecast - accelerating pipeline
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_executive_dashboard_accelerating_pipeline():
    service, db = make_service()

    db.execute.side_effect = [
        make_scalar_result(100),
        make_scalar_result(50),
        make_scalar_result(20),
        make_scalar_result(100),  # submissions >= 100
        make_scalar_result(15),
        make_scalar_result(30),
        make_scalar_result(10),
        make_recruiter_result([]),
    ]

    result = await service.build_executive_dashboard()

    assert result.forecast.expected_placements_this_month == 16
    assert result.forecast.pipeline_growth_velocity == "ACCELERATING"