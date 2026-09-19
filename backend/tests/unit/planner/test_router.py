from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.planner.router import (
    get_daily_planner,
    get_planner_service,
)


@pytest.mark.asyncio
async def test_get_planner_service():
    db = MagicMock()

    result = await get_planner_service(db)

    assert result.db is db


@pytest.mark.asyncio
async def test_get_daily_planner_with_explicit_date():
    service = MagicMock()
    service.get_daily_plan = AsyncMock(
        return_value="daily-plan"
    )

    current_user = MagicMock()
    current_user.id = 123

    planner_date = date(2026, 9, 18)

    result = await get_daily_planner(
        planner_date=planner_date,
        current_user=current_user,
        service=service,
        _role="RECRUITER",
    )

    assert result == "daily-plan"

    service.get_daily_plan.assert_awaited_once_with(
        user_id=123,
        planner_date=planner_date,
    )


@pytest.mark.asyncio
async def test_get_daily_planner_defaults_to_today():
    service = MagicMock()
    service.get_daily_plan = AsyncMock(
        return_value="daily-plan"
    )

    current_user = MagicMock()
    current_user.id = 456

    result = await get_daily_planner(
        planner_date=None,
        current_user=current_user,
        service=service,
        _role="MANAGER",
    )

    assert result == "daily-plan"

    service.get_daily_plan.assert_awaited_once_with(
        user_id=456,
        planner_date=date.today(),
    )