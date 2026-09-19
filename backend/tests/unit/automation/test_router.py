from unittest.mock import AsyncMock, MagicMock

import pytest

from app.automation.router import (
    get_automation_service,
    create_background_workflow_rule,
    list_rule_execution_logs,
)
from app.automation.service import WorkflowAutomationService
from app.automation.schemas import WorkflowRuleCreateRequest
from app.automation.enums import AutomationTriggerType


def get_trigger_type():
    return next(iter(AutomationTriggerType))


@pytest.mark.asyncio
async def test_get_automation_service_creates_service():
    db = MagicMock()

    service = await get_automation_service(db=db)

    assert isinstance(service, WorkflowAutomationService)
    assert service.db is db


@pytest.mark.asyncio
async def test_create_background_workflow_rule_delegates_to_service():
    trigger_type = get_trigger_type()

    payload = WorkflowRuleCreateRequest(
        name="Test Workflow",
        trigger_type=trigger_type,
        condition_json={"status": "OPEN"},
        action_json={"action": "NOTIFY"},
        priority=5,
    )

    expected_response = MagicMock()

    service = MagicMock()
    service.register_workflow_rule = AsyncMock(
        return_value=expected_response
    )

    result = await create_background_workflow_rule(
        payload=payload,
        service=service,
        _role=MagicMock(),
    )

    assert result is expected_response

    service.register_workflow_rule.assert_awaited_once_with(
        payload=payload
    )


@pytest.mark.asyncio
async def test_list_rule_execution_logs_delegates_to_service():
    expected_logs = [MagicMock(), MagicMock()]

    service = MagicMock()
    service.get_rule_execution_logs = AsyncMock(
        return_value=expected_logs
    )

    result = await list_rule_execution_logs(
        service=service,
        _role=MagicMock(),
    )

    assert result == expected_logs

    service.get_rule_execution_logs.assert_awaited_once_with()