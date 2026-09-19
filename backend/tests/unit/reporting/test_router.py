from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.reporting.router import (
    create_saved_report_profile,
    execute_report_generation,
    get_reporting_service,
    list_report_execution_history,
)


@pytest.mark.asyncio
async def test_get_reporting_service():
    db = MagicMock()

    result = await get_reporting_service(db)

    assert result.db is db


@pytest.mark.asyncio
async def test_create_saved_report_profile():
    service = MagicMock()
    service.create_report_definition = AsyncMock(
        return_value="report-definition"
    )

    payload = MagicMock()
    current_user = MagicMock()
    current_user.id = 123

    result = await create_saved_report_profile(
        payload=payload,
        current_user=current_user,
        service=service,
        _role="ADMIN",
    )

    assert result == "report-definition"

    service.create_report_definition.assert_awaited_once_with(
        payload=payload,
        user_id=123,
    )


@pytest.mark.asyncio
async def test_execute_report_generation():
    service = MagicMock()
    service.trigger_on_demand_execution = AsyncMock(
        return_value="execution"
    )

    public_id = uuid4()

    current_user = MagicMock()
    current_user.id = 456

    result = await execute_report_generation(
        public_id=public_id,
        current_user=current_user,
        service=service,
        _role="MANAGER",
    )

    assert result == "execution"

    service.trigger_on_demand_execution.assert_awaited_once_with(
        public_id=public_id,
        executioner_user_id=456,
    )


@pytest.mark.asyncio
async def test_list_report_execution_history():
    service = MagicMock()
    service.fetch_execution_history_logs = AsyncMock(
        return_value=["execution-1", "execution-2"]
    )

    result = await list_report_execution_history(
        service=service,
        _role="ADMIN",
    )

    assert result == ["execution-1", "execution-2"]

    service.fetch_execution_history_logs.assert_awaited_once_with()