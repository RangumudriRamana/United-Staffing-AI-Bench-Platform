from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

from app.core.exceptions import AppException
from app.reporting.enums import ReportExecutionStatus
from app.reporting.service import ReportingService


def make_service():
    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()

    service = ReportingService(db)

    service.audit_service = MagicMock()
    service.audit_service.write_audit_entry = AsyncMock()
    service.audit_service.get_next_entity_version = AsyncMock(
        return_value=1
    )

    return service, db


def make_definition():
    return SimpleNamespace(
        id=10,
        public_id=UUID("11111111-1111-1111-1111-111111111111"),
        name="Vendor Report",
        report_type=SimpleNamespace(value="VENDOR_ANALYTICS"),
        output_format=SimpleNamespace(value="CSV"),
        parameters_json={},
        schedule=None,
    )


# ---------------------------------------------------------------------------
# create_report_definition
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_report_definition_success():
    service, db = make_service()

    payload = SimpleNamespace(
        name="Vendor Report",
        report_type=SimpleNamespace(value="VENDOR_ANALYTICS"),
        output_format=SimpleNamespace(value="CSV"),
        parameters_json={"vendor_id": "123"},
        schedule="0 9 * * *",
    )

    fake_definition = MagicMock()
    fake_definition.name = "Vendor Report"
    fake_definition.created_by = 99
    fake_definition.is_enabled = True

    with patch(
        "app.reporting.service.ReportDefinition",
        return_value=fake_definition,
    ) as definition_cls:
        result = await service.create_report_definition(
            payload=payload,
            user_id=99,
        )

    assert result is fake_definition

    definition_cls.assert_called_once_with(
        name="Vendor Report",
        report_type=payload.report_type,
        output_format=payload.output_format,
        parameters_json={"vendor_id": "123"},
        schedule="0 9 * * *",
        created_by=99,
        is_enabled=True,
    )

    db.add.assert_called_once_with(fake_definition)
    db.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# trigger_on_demand_execution
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_trigger_on_demand_execution_definition_not_found():
    service, db = make_service()

    result = MagicMock()
    result.scalars.return_value.first.return_value = None
    db.execute.return_value = result

    public_id = UUID("11111111-1111-1111-1111-111111111111")

    with pytest.raises(AppException) as exc:
        await service.trigger_on_demand_execution(
            public_id=public_id,
            executioner_user_id=99,
        )

    assert exc.value.status_code == 404
    assert (
        exc.value.message
        == "Target report template layout configuration not found."
    )

    db.flush.assert_not_awaited()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_trigger_on_demand_execution_success():
    service, db = make_service()

    definition = make_definition()

    definition_result = MagicMock()
    definition_result.scalars.return_value.first.return_value = definition
    db.execute.return_value = definition_result

    fake_execution = MagicMock()
    fake_execution.id = 42
    fake_execution.status = None
    fake_execution.file_location = None
    fake_execution.duration_ms = None

    with patch(
        "app.reporting.service.ReportExecution",
        return_value=fake_execution,
    ) as execution_cls:
        result = await service.trigger_on_demand_execution(
            public_id=definition.public_id,
            executioner_user_id=99,
        )

    assert result is fake_execution
    assert fake_execution.status == ReportExecutionStatus.SUCCESS
    assert (
        fake_execution.file_location
        == "/var/storage/exports/vendor_analytics_42.csv"
    )
    assert fake_execution.duration_ms >= 1

    execution_cls.assert_called_once_with(
        report_definition_id=10,
        generated_by=99,
        status=ReportExecutionStatus.RUNNING,
    )

    db.add.assert_called_once_with(fake_execution)
    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()

    service.audit_service.write_audit_entry.assert_awaited_once()
    service.audit_service.get_next_entity_version.assert_awaited_once_with(
        entity_type="REPORT_DEFINITION",
        entity_public_id=str(definition.public_id),
    )


@pytest.mark.asyncio
async def test_trigger_on_demand_execution_audit_failure_marks_execution_failed():
    service, db = make_service()

    definition = make_definition()

    definition_result = MagicMock()
    definition_result.scalars.return_value.first.return_value = definition
    db.execute.return_value = definition_result

    fake_execution = MagicMock()
    fake_execution.id = 77
    fake_execution.status = None
    fake_execution.file_location = None
    fake_execution.duration_ms = None

    service.audit_service.write_audit_entry.side_effect = RuntimeError(
        "audit failure"
    )

    with patch(
        "app.reporting.service.ReportExecution",
        return_value=fake_execution,
    ):
        with pytest.raises(RuntimeError, match="audit failure"):
            await service.trigger_on_demand_execution(
                public_id=definition.public_id,
                executioner_user_id=99,
            )

    assert fake_execution.status == ReportExecutionStatus.FAILED
    assert fake_execution.error_message == "audit failure"

    db.rollback.assert_awaited_once()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_trigger_on_demand_execution_truncates_long_error_message():
    service, db = make_service()

    definition = make_definition()

    definition_result = MagicMock()
    definition_result.scalars.return_value.first.return_value = definition
    db.execute.return_value = definition_result

    fake_execution = MagicMock()
    fake_execution.id = 88
    fake_execution.status = None
    fake_execution.file_location = None
    fake_execution.duration_ms = None

    long_error = "X" * 700

    service.audit_service.write_audit_entry.side_effect = RuntimeError(
        long_error
    )

    with patch(
        "app.reporting.service.ReportExecution",
        return_value=fake_execution,
    ):
        with pytest.raises(RuntimeError):
            await service.trigger_on_demand_execution(
                public_id=definition.public_id,
                executioner_user_id=99,
            )

    assert fake_execution.status == ReportExecutionStatus.FAILED
    assert len(fake_execution.error_message) == 499
    assert fake_execution.error_message == long_error[:499]

    db.rollback.assert_awaited_once()
    db.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# fetch_execution_history_logs
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_execution_history_logs_returns_records():
    service, db = make_service()

    execution_1 = MagicMock()
    execution_2 = MagicMock()

    result = MagicMock()
    result.scalars.return_value.all.return_value = [
        execution_1,
        execution_2,
    ]
    db.execute.return_value = result

    records = await service.fetch_execution_history_logs(limit=25)

    assert records == [execution_1, execution_2]
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_execution_history_logs_returns_empty_list():
    service, db = make_service()

    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    db.execute.return_value = result

    records = await service.fetch_execution_history_logs()

    assert records == []
    db.execute.assert_awaited_once()