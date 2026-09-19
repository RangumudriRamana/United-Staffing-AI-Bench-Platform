from unittest.mock import AsyncMock, MagicMock

import pytest

from app.analytics.dashboard.router import (
    get_authenticated_recruiter_workspace,
    get_dashboard_service,
)


@pytest.mark.asyncio
async def test_get_dashboard_service_creates_service():
    db = MagicMock()

    service = await get_dashboard_service(db=db)

    from app.analytics.dashboard.service import RecruiterDashboardService

    assert isinstance(service, RecruiterDashboardService)
    assert service.db is db


@pytest.mark.asyncio
async def test_get_authenticated_recruiter_workspace_delegates_to_service():
    current_user = MagicMock()
    current_user.id = 123

    expected_response = MagicMock()

    service = MagicMock()
    service.build_recruiter_dashboard = AsyncMock(
        return_value=expected_response
    )

    result = await get_authenticated_recruiter_workspace(
        current_user=current_user,
        service=service,
        _role=MagicMock(),
    )

    assert result is expected_response

    service.build_recruiter_dashboard.assert_awaited_once_with(
        recruiter_id=123
    )