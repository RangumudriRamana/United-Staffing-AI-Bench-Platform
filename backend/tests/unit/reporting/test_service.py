from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.exceptions import AppException
from app.reporting.enums import ReportExecutionStatus
from app.reporting.service import ReportingService


def make_service():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.flush = AsyncMock()
    db.rollback = AsyncMock()
    db.execute = AsyncMock()

    service = ReportingService(db)

    service.audit_service.write_audit_entry = AsyncMock()
    service.audit_service.get_next_entity_version = AsyncMock(
        return_value=1
    )

    return db, service


def scalar_result(value):
    result = MagicMock()
    result.scalars.return_value.first.return_value = value
    return result


def make_definition():
    return SimpleNamespace(
        id=10,
        public_id=uuid4(),
        report_type=SimpleNamespace(value="CONSULTANT"),
        output_format=SimpleNamespace(value="CSV"),
    )


@pytest.mark.asyncio
async def test_create_report_definition():
    db, service = make_service()

    payload = SimpleNamespace(
        name="Consultant Report",
        report_type=SimpleNamespace(value="CONSULTANT"),
        output_format=SimpleNamespace(value="CSV"),
        parameters_json={"status": "AVAILABLE"},
        schedule="DAILY",
    )

    result = await service.create_report_definition(
        payload=payload,
        user_id=25,
    )

    db.add.assert_called_once()
    db.commit.assert_awaited_once()

    assert result.name == "Consultant Report"
    assert result.report_type is payload.report_type
    assert result.output_format is payload.output_format
    assert result.parameters_json == {"status": "AVAILABLE"}
    assert result.schedule == "DAILY"
    assert result.created_by == 25
    assert result.is_enabled is True


@pytest.mark.asyncio
async def test_trigger_on_demand_execution_success():
    db, service = make_service()

    definition = make_definition()

    db.execute.return_value = scalar_result(definition)

    result = await service.trigger_on_demand_execution(
        public_id=definition.public_id,
        executioner_user_id=99,
    )

    db.add.assert_called_once()
    db.flush.assert_awaited_once()

    execution = db.add.call_args.args[0]

    assert execution.report_definition_id == 10
    assert execution.generated_by == 99
    assert execution.status == ReportExecutionStatus.SUCCESS
    assert execution.file_location.startswith(
        "/var/storage/exports/consultant_"
    )
    assert execution.file_location.endswith(".csv")
    assert execution.duration_ms >= 1

    service.audit_service.get_next_entity_version.assert_awaited_once_with(
        entity_type="REPORT_DEFINITION",
        entity_public_id=str(definition.public_id),
    )

    service.audit_service.write_audit_entry.assert_awaited_once()

    db.commit.assert_awaited_once()

    assert result is execution


@pytest.mark.asyncio
async def test_trigger_on_demand_execution_definition_not_found():
    db, service = make_service()

    db.execute.return_value = scalar_result(None)

    with pytest.raises(AppException) as exc_info:
        await service.trigger_on_demand_execution(
            public_id=uuid4(),
            executioner_user_id=99,
        )

    assert exc_info.value.status_code == 404
    db.add.assert_not_called()
    db.flush.assert_not_awaited()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_trigger_on_demand_execution_audit_failure():
    db, service = make_service()

    definition = make_definition()
    db.execute.return_value = scalar_result(definition)

    service.audit_service.write_audit_entry.side_effect = RuntimeError(
        "audit failure"
    )

    with pytest.raises(RuntimeError, match="audit failure"):
        await service.trigger_on_demand_execution(
            public_id=definition.public_id,
            executioner_user_id=99,
        )

    db.rollback.assert_awaited_once()
    assert db.commit.await_count == 1

    execution = db.add.call_args.args[0]

    assert execution.status == ReportExecutionStatus.FAILED
    assert execution.error_message == "audit failure"


@pytest.mark.asyncio
async def test_fetch_execution_history_logs():
    db, service = make_service()

    executions = [
        SimpleNamespace(id=1),
        SimpleNamespace(id=2),
    ]

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.all.return_value = executions
    db.execute.return_value = result_proxy

    result = await service.fetch_execution_history_logs(limit=25)

    assert result == executions
    assert len(result) == 2
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_execution_history_logs_empty():
    db, service = make_service()

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.all.return_value = []
    db.execute.return_value = result_proxy

    result = await service.fetch_execution_history_logs()

    assert result == []