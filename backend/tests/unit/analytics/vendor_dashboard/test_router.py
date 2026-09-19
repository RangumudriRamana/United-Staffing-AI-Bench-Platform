from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.analytics.vendor_dashboard.router import (
    get_vendor_analytics_service,
    get_vendor_relationship_metrics,
)
from app.analytics.vendor_dashboard.service import VendorAnalyticsService


@pytest.mark.asyncio
async def test_get_vendor_analytics_service_creates_service():
    db = MagicMock()

    service = await get_vendor_analytics_service(db=db)

    assert isinstance(service, VendorAnalyticsService)
    assert service.db is db


@pytest.mark.asyncio
async def test_get_vendor_relationship_metrics_delegates_to_service():
    vendor_public_id = uuid4()
    expected_response = MagicMock()

    service = MagicMock()
    service.generate_vendor_profile_analytics = AsyncMock(
        return_value=expected_response
    )

    result = await get_vendor_relationship_metrics(
        vendor_public_id=vendor_public_id,
        service=service,
        _role=MagicMock(),
    )

    assert result is expected_response

    service.generate_vendor_profile_analytics.assert_awaited_once_with(
        vendor_public_id=vendor_public_id
    )