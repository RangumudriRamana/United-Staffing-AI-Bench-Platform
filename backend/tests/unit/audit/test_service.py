from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.audit.service import AuditService


def make_db():
    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    return db


def make_result(
    scalar_one_or_none=None,
    scalars_all=None,
):
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_one_or_none

    scalars = MagicMock()
    scalars.all.return_value = scalars_all or []
    result.scalars.return_value = scalars

    return result


@pytest.mark.asyncio
async def test_get_next_entity_version_returns_one_when_no_history():
    db = make_db()
    db.execute.return_value = make_result(
        scalar_one_or_none=None
    )

    service = AuditService(db)

    result = await service.get_next_entity_version(
        "consultant",
        str(uuid4()),
    )

    assert result == 1
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_next_entity_version_increments_existing_version():
    db = make_db()
    db.execute.return_value = make_result(
        scalar_one_or_none=5
    )

    service = AuditService(db)

    result = await service.get_next_entity_version(
        "CONSULTANT",
        str(uuid4()),
    )

    assert result == 6
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_write_audit_entry_normalizes_fields_and_flushes():
    db = make_db()

    actor_id = uuid4()
    entity_id = uuid4()
    correlation_id = uuid4()

    payload = SimpleNamespace(
        actor_user_id=actor_id,
        action_type="CREATE",
        source_context=" api ",
        correlation_id=str(correlation_id),
        entity_type=" consultant ",
        entity_public_id=entity_id,
        entity_version=3,
        before_snapshot_json={"old": "value"},
        after_snapshot_json={"new": "value"},
        metadata_json={"source": "test"},
    )

    service = AuditService(db)

    result = await service.write_audit_entry(payload)

    assert result.actor_user_id == actor_id
    assert result.action_type == "CREATE"
    assert result.source_context == "API"
    assert result.correlation_id == str(correlation_id)
    assert result.entity_type == "CONSULTANT"
    assert result.entity_public_id == str(entity_id)
    assert result.entity_version == 3
    assert result.before_snapshot_json == {"old": "value"}
    assert result.after_snapshot_json == {"new": "value"}
    assert result.metadata_json == {"source": "test"}

    db.add.assert_called_once_with(result)
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_write_audit_entry_uses_context_correlation_id():
    db = make_db()

    payload = SimpleNamespace(
        actor_user_id=None,
        action_type="UPDATE",
        source_context="system",
        correlation_id=None,
        entity_type="vendor",
        entity_public_id=uuid4(),
        entity_version=2,
        before_snapshot_json=None,
        after_snapshot_json={"status": "active"},
        metadata_json=None,
    )

    service = AuditService(db)

    from app.audit.service import correlation_id_ctx

    token = correlation_id_ctx.set("context-correlation-id")

    try:
        result = await service.write_audit_entry(payload)
    finally:
        correlation_id_ctx.reset(token)

    assert result.correlation_id == "context-correlation-id"
    db.add.assert_called_once_with(result)
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_write_audit_entry_uses_none_when_no_correlation_id():
    db = make_db()

    payload = SimpleNamespace(
        actor_user_id=None,
        action_type="DELETE",
        source_context="system",
        correlation_id=None,
        entity_type="vendor",
        entity_public_id=uuid4(),
        entity_version=1,
        before_snapshot_json=None,
        after_snapshot_json=None,
        metadata_json=None,
    )

    service = AuditService(db)

    from app.audit.service import correlation_id_ctx

    token = correlation_id_ctx.set(None)

    try:
        result = await service.write_audit_entry(payload)
    finally:
        correlation_id_ctx.reset(token)

    assert result.correlation_id is None
    db.add.assert_called_once_with(result)
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_entity_version_history_returns_records():
    db = make_db()

    records = [
        SimpleNamespace(entity_version=2),
        SimpleNamespace(entity_version=1),
    ]

    db.execute.return_value = make_result(
        scalars_all=records
    )

    service = AuditService(db)

    result = await service.fetch_entity_version_history(
        " consultant ",
        "entity-123",
    )

    assert result == records
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_entity_version_history_returns_empty_list():
    db = make_db()
    db.execute.return_value = make_result(
        scalars_all=[]
    )

    service = AuditService(db)

    result = await service.fetch_entity_version_history(
        "vendor",
        "entity-123",
    )

    assert result == []
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolve_correlation_chain_returns_records():
    db = make_db()

    records = [
        SimpleNamespace(action_type="CREATE"),
        SimpleNamespace(action_type="UPDATE"),
    ]

    db.execute.return_value = make_result(
        scalars_all=records
    )

    service = AuditService(db)

    result = await service.resolve_correlation_chain(
        "correlation-123"
    )

    assert result == records
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolve_correlation_chain_returns_empty_list():
    db = make_db()
    db.execute.return_value = make_result(
        scalars_all=[]
    )

    service = AuditService(db)

    result = await service.resolve_correlation_chain(
        "missing-correlation"
    )

    assert result == []
    db.execute.assert_awaited_once()