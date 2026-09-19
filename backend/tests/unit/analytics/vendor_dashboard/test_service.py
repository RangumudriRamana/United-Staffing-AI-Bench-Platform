from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.analytics.enums import BusinessEventType
from app.analytics.vendor_dashboard.service import VendorAnalyticsService
from app.core.exceptions import AppException


def make_service():
    db = MagicMock()
    service = VendorAnalyticsService(db)
    return service, db


@pytest.mark.asyncio
async def test_generate_vendor_profile_analytics_vendor_not_found():
    service, db = make_service()

    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = None
    db.execute = AsyncMock(return_value=result_mock)

    with pytest.raises(AppException) as exc_info:
        await service.generate_vendor_profile_analytics(uuid4())

    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "Target vendor profile record not found."

    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_vendor_profile_analytics_builds_funnel_and_health():
    service, db = make_service()

    vendor_public_id = uuid4()
    vendor = MagicMock()
    vendor.id = 10
    vendor.public_id = vendor_public_id
    vendor.name = "Test Vendor"

    vendor_result = MagicMock()
    vendor_result.scalars.return_value.first.return_value = vendor
    db.execute = AsyncMock(return_value=vendor_result)

    service._get_event_count_by_vendor = AsyncMock(
        side_effect=[10, 20, 5, 2]
    )

    result = await service.generate_vendor_profile_analytics(
        vendor_public_id
    )

    assert result.vendor_public_id == vendor_public_id
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
    assert len(result.health.contributing_factors) == 2

    assert result.velocity.avg_days_req_to_submission == 2.4
    assert result.velocity.avg_days_submission_to_interview == 4.1
    assert result.velocity.avg_days_interview_to_feedback == 1.8

    service._get_event_count_by_vendor.assert_has_awaits(
        [
            ((10, BusinessEventType.REQUIREMENT_OPENED),),
            ((10, BusinessEventType.SUBMISSION_CREATED),),
            ((10, BusinessEventType.INTERVIEW_SCHEDULED),),
            ((10, BusinessEventType.PLACEMENT_CREATED),),
        ]
    )


@pytest.mark.asyncio
async def test_generate_vendor_profile_analytics_handles_zero_denominators():
    service, db = make_service()

    vendor = MagicMock()
    vendor.id = 20
    vendor.public_id = uuid4()
    vendor.name = "Zero Vendor"

    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = vendor
    db.execute = AsyncMock(return_value=result_mock)

    service._get_event_count_by_vendor = AsyncMock(
        side_effect=[0, 0, 0, 0]
    )

    result = await service.generate_vendor_profile_analytics(
        vendor.public_id
    )

    assert [stage.count for stage in result.funnel] == [0, 0, 0, 0]
    assert [stage.conversion_rate for stage in result.funnel] == [
        100.0,
        0.0,
        0.0,
        0.0,
    ]

    assert result.health.health_score == 25
    assert result.health.status_label == "AT_RISK"


@pytest.mark.asyncio
async def test_get_event_count_by_vendor_returns_count():
    service, db = make_service()

    result_mock = MagicMock()
    result_mock.scalar.return_value = 7
    db.execute = AsyncMock(return_value=result_mock)

    result = await service._get_event_count_by_vendor(
        vendor_id=10,
        event_type=BusinessEventType.SUBMISSION_CREATED,
    )

    assert result == 7
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_event_count_by_vendor_returns_zero_for_none():
    service, db = make_service()

    result_mock = MagicMock()
    result_mock.scalar.return_value = None
    db.execute = AsyncMock(return_value=result_mock)

    result = await service._get_event_count_by_vendor(
        vendor_id=10,
        event_type=BusinessEventType.SUBMISSION_CREATED,
    )

    assert result == 0


def test_calculate_account_health_high_submissions_with_placement():
    service, _ = make_service()

    result = service._calculate_account_health(
        submission_count=16,
        placement_count=1,
    )

    assert result.health_score == 100
    assert result.status_label == "STRATEGIC"
    assert len(result.contributing_factors) == 2


def test_calculate_account_health_low_submissions_with_placement():
    service, _ = make_service()

    result = service._calculate_account_health(
        submission_count=10,
        placement_count=1,
    )

    assert result.health_score == 70
    assert result.status_label == "ACTIVE"
    assert len(result.contributing_factors) == 2


def test_calculate_account_health_high_submissions_without_placement():
    service, _ = make_service()

    result = service._calculate_account_health(
        submission_count=16,
        placement_count=0,
    )

    assert result.health_score == 55
    assert result.status_label == "ACTIVE"
    assert len(result.contributing_factors) == 2


def test_calculate_account_health_low_submissions_without_placement():
    service, _ = make_service()

    result = service._calculate_account_health(
        submission_count=10,
        placement_count=0,
    )

    assert result.health_score == 25
    assert result.status_label == "AT_RISK"
    assert len(result.contributing_factors) == 2