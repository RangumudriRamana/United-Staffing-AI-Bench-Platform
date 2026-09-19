from unittest.mock import AsyncMock, MagicMock

import pytest

from app.analytics.executive.router import (
    get_executive_service,
    get_firm_wide_executive_dashboard,
)
from app.analytics.executive.service import ExecutiveDashboardService


@pytest.mark.asyncio
async def test_get_executive_service_creates_service():
    db = MagicMock()

    service = await get_executive_service(db=db)

    assert isinstance(service, ExecutiveDashboardService)
    assert service.db is db


@pytest.mark.asyncio
async def test_get_firm_wide_executive_dashboard_delegates_to_service():
    expected_response = MagicMock()

    service = MagicMock()
    service.build_executive_dashboard = AsyncMock(
        return_value=expected_response
    )

    result = await get_firm_wide_executive_dashboard(
        service=service,
        _role=MagicMock(),
    )

    assert result is expected_response

    service.build_executive_dashboard.assert_awaited_once_with()