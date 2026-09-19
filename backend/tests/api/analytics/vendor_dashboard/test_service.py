from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from app.analytics.enums import BusinessEventType
from app.analytics.vendor_dashboard.service import VendorAnalyticsService
from app.core.exceptions import AppException


def make_service():
    db = MagicMock()
    db.execute = AsyncMock()

    service = VendorAnalyticsService(db)

    return service, db


def make_vendor():
    return SimpleNamespace(
        id=10,
        public_id=UUID("11111111-1111-1111-1111-111111111111"),
        name="Test Vendor",
    )


# ---------------------------------------------------------------------------
# generate_vendor_profile_analytics
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_vendor_profile_analytics_success():
    service, db = make_service()

    vendor = make_vendor()

    vendor_result = MagicMock()
    vendor_result.scalars.return_value.first.return_value = vendor
    db.execute.return_value = vendor_result

    service._get_event_count_by_vendor = AsyncMock(
        side_effect=[
            10,  # requirements
            20,  # submissions
            5,   # interviews
            2,   # placements
        ]
    )

    result = await service.generate_vendor_profile_analytics(
        vendor.public_id
    )

    assert result.vendor_public_id == vendor.public_id
    assert result.vendor_name == "Test Vendor"

    assert len(result.funnel) == 4

    assert result.funnel[0].stage_name == "Requirements"
    assert result.funnel[0].count == 10
    assert result.funnel[0].conversion_rate == 100.0

    assert result.funnel[1].stage_name == "Submissions"
    assert result.funnel[1].count == 20
    assert result.funnel[1].conversion_rate == 200.0

    assert result.funnel[2].stage_name == "Interviews"
    assert result.funnel[2].count == 5
    assert result.funnel[2].conversion_rate == 25.0

    assert result.funnel[3].stage_name == "Placements"
    assert result.funnel[3].count == 2
    assert result.funnel[3].conversion_rate == 40.0

    assert result.health.health_score == 100
    assert result.health.status_label == "STRATEGIC"

    assert result.velocity.avg_days_req_to_submission == 2.4
    assert result.velocity.avg_days_submission_to_interview == 4.1
    assert result.velocity.avg_days_interview_to_feedback == 1.8

    assert service._get_event_count_by_vendor.await_count == 4


@pytest.mark.asyncio
async def test_generate_vendor_profile_analytics_vendor_not_found():
    service, db = make_service()

    vendor_result = MagicMock()
    vendor_result.scalars.return_value.first.return_value = None
    db.execute.return_value = vendor_result

    with pytest.raises(AppException) as exc:
        await service.generate_vendor_profile_analytics(
            UUID("11111111-1111-1111-1111-111111111111")
        )

    assert exc.value.status_code == 404
    assert exc.value.message == "Target vendor profile record not found."


@pytest.mark.asyncio
async def test_generate_vendor_profile_analytics_zero_funnel_counts():
    service, db = make_service()

    vendor = make_vendor()

    vendor_result = MagicMock()
    vendor_result.scalars.return_value.first.return_value = vendor
    db.execute.return_value = vendor_result

    service._get_event_count_by_vendor = AsyncMock(
        return_value=0
    )

    result = await service.generate_vendor_profile_analytics(
        vendor.public_id
    )

    assert len(result.funnel) == 4

    for stage in result.funnel:
        assert stage.count == 0

    assert result.funnel[0].conversion_rate == 100.0
    assert result.funnel[1].conversion_rate == 0.0
    assert result.funnel[2].conversion_rate == 0.0
    assert result.funnel[3].conversion_rate == 0.0

    assert result.health.health_score == 25
    assert result.health.status_label == "AT_RISK"


# ---------------------------------------------------------------------------
# _get_event_count_by_vendor
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_event_count_by_vendor_returns_count():
    service, db = make_service()

    result = MagicMock()
    result.scalar.return_value = 17
    db.execute.return_value = result

    count = await service._get_event_count_by_vendor(
        vendor_id=10,
        event_type=BusinessEventType.REQUIREMENT_OPENED,
    )

    assert count == 17
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_event_count_by_vendor_returns_zero_for_none():
    service, db = make_service()

    result = MagicMock()
    result.scalar.return_value = None
    db.execute.return_value = result

    count = await service._get_event_count_by_vendor(
        vendor_id=10,
        event_type=BusinessEventType.REQUIREMENT_OPENED,
    )

    assert count == 0


@pytest.mark.asyncio
async def test_get_event_count_by_vendor_returns_zero_for_zero():
    service, db = make_service()

    result = MagicMock()
    result.scalar.return_value = 0
    db.execute.return_value = result

    count = await service._get_event_count_by_vendor(
        vendor_id=10,
        event_type=BusinessEventType.SUBMISSION_CREATED,
    )

    assert count == 0


# ---------------------------------------------------------------------------
# _calculate_account_health
# ---------------------------------------------------------------------------


def test_calculate_account_health_strategic():
    service, _ = make_service()

    result = service._calculate_account_health(
        submission_count=16,
        placement_count=1,
    )

    assert result.health_score == 100
    assert result.status_label == "STRATEGIC"
    assert len(result.contributing_factors) == 2
    assert "High submission velocity" in result.contributing_factors[0]
    assert "Proven placement history" in result.contributing_factors[1]


def test_calculate_account_health_active_high_submissions_no_placements():
    service, _ = make_service()

    result = service._calculate_account_health(
        submission_count=16,
        placement_count=0,
    )

    assert result.health_score == 55
    assert result.status_label == "ACTIVE"
    assert len(result.contributing_factors) == 2
    assert "High submission velocity" in result.contributing_factors[0]
    assert "Zero placement conversions" in result.contributing_factors[1]


def test_calculate_account_health_active_low_submissions_with_placement():
    service, _ = make_service()

    result = service._calculate_account_health(
        submission_count=15,
        placement_count=1,
    )

    assert result.health_score == 70
    assert result.status_label == "ACTIVE"
    assert len(result.contributing_factors) == 2
    assert "Low transaction volume" in result.contributing_factors[0]
    assert "Proven placement history" in result.contributing_factors[1]


def test_calculate_account_health_at_risk():
    service, _ = make_service()

    result = service._calculate_account_health(
        submission_count=15,
        placement_count=0,
    )

    assert result.health_score == 25
    assert result.status_label == "AT_RISK"
    assert len(result.contributing_factors) == 2
    assert "Low transaction volume" in result.contributing_factors[0]
    assert "Zero placement conversions" in result.contributing_factors[1]