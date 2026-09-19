from unittest.mock import AsyncMock, MagicMock

import pytest

from app.automation.enums import AutomationTriggerType, ExecutionStatus
from app.automation.models import WorkflowExecution, WorkflowRule
from app.automation.schemas import WorkflowRuleCreateRequest
from app.automation.service import WorkflowAutomationService


def make_service():
    db = MagicMock()
    db.commit = AsyncMock()
    db.execute = AsyncMock()
    service = WorkflowAutomationService(db)
    return service, db


def get_trigger_type():
    return next(iter(AutomationTriggerType))


@pytest.mark.asyncio
async def test_register_workflow_rule_creates_and_commits_rule():
    service, db = make_service()

    trigger_type = get_trigger_type()

    payload = WorkflowRuleCreateRequest(
        name="Test Workflow",
        trigger_type=trigger_type,
        condition_json={"status": "OPEN"},
        action_json={"action": "NOTIFY"},
        priority=5,
    )

    result = await service.register_workflow_rule(payload)

    assert isinstance(result, WorkflowRule)
    assert result.name == "Test Workflow"
    assert result.trigger_type == trigger_type
    assert result.condition_json == {"status": "OPEN"}
    assert result.action_json == {"action": "NOTIFY"}
    assert result.priority == 5
    assert result.is_enabled is True

    db.add.assert_called_once_with(result)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_workflow_rule_supports_default_optional_values():
    service, db = make_service()

    trigger_type = get_trigger_type()

    payload = WorkflowRuleCreateRequest(
        name="Minimal Workflow",
        trigger_type=trigger_type,
        action_json={"action": "LOG"},
    )

    result = await service.register_workflow_rule(payload)

    assert result.name == "Minimal Workflow"
    assert result.condition_json is None
    assert result.action_json == {"action": "LOG"}
    assert result.priority == 1
    assert result.is_enabled is True

    db.add.assert_called_once_with(result)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_system_trigger_returns_zero_when_no_active_rules():
    service, db = make_service()

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=result_mock)

    trigger_type = get_trigger_type()

    result = await service.process_system_trigger(
        trigger_type=trigger_type,
        context_metadata={"source": "test"},
    )

    assert result == 0
    db.add.assert_not_called()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_system_trigger_creates_success_execution_logs():
    service, db = make_service()

    trigger_type = get_trigger_type()

    rule = MagicMock()
    rule.id = 101

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [rule]
    db.execute = AsyncMock(return_value=result_mock)

    result = await service.process_system_trigger(
        trigger_type=trigger_type,
        context_metadata={"source": "test"},
    )

    assert result == 1

    db.add.assert_called_once()

    execution = db.add.call_args.args[0]

    assert isinstance(execution, WorkflowExecution)
    assert execution.workflow_rule_id == 101
    assert execution.trigger_event_type == trigger_type.value
    assert execution.status == ExecutionStatus.SUCCESS
    assert execution.duration_ms >= 1
    assert execution.error_message is None

    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_system_trigger_processes_multiple_rules():
    service, db = make_service()

    trigger_type = get_trigger_type()

    rule_one = MagicMock()
    rule_one.id = 101

    rule_two = MagicMock()
    rule_two.id = 202

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [
        rule_one,
        rule_two,
    ]
    db.execute = AsyncMock(return_value=result_mock)

    result = await service.process_system_trigger(
        trigger_type=trigger_type,
        context_metadata={"event": "test"},
    )

    assert result == 2
    assert db.add.call_count == 2
    assert db.commit.await_count == 1

    added_executions = [
        call.args[0] for call in db.add.call_args_list
    ]

    assert all(
        isinstance(execution, WorkflowExecution)
        for execution in added_executions
    )

    assert [execution.workflow_rule_id for execution in added_executions] == [
        101,
        202,
    ]


@pytest.mark.asyncio
async def test_get_rule_execution_logs_returns_latest_logs():
    service, db = make_service()

    execution_one = MagicMock()
    execution_two = MagicMock()

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [
        execution_one,
        execution_two,
    ]
    db.execute = AsyncMock(return_value=result_mock)

    result = await service.get_rule_execution_logs(limit=10)

    assert result == [
        execution_one,
        execution_two,
    ]

    db.execute.assert_awaited_once()