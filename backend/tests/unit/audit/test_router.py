from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI

from app.audit.router import (
    get_audit_service,
    get_polymorphic_entity_audit_trail,
    get_transaction_correlation_chain,
)


@pytest.mark.asyncio
async def test_get_audit_service():
    db = MagicMock()

    result = await get_audit_service(db)

    assert result.db is db


@pytest.mark.asyncio
async def test_get_polymorphic_entity_audit_trail():
    service = MagicMock()
    service.fetch_entity_version_history = AsyncMock(
        return_value=["record-1", "record-2"]
    )

    entity_id = str(uuid4())

    result = await get_polymorphic_entity_audit_trail(
        entity_type="consultant",
        entity_public_id=entity_id,
        service=service,
        _role="ADMIN",
    )

    assert result == ["record-1", "record-2"]

    service.fetch_entity_version_history.assert_awaited_once_with(
        entity_type="consultant",
        entity_public_id=entity_id,
    )


@pytest.mark.asyncio
async def test_get_transaction_correlation_chain():
    service = MagicMock()
    service.resolve_correlation_chain = AsyncMock(
        return_value=["record-1", "record-2"]
    )

    result = await get_transaction_correlation_chain(
        correlation_id="correlation-123",
        service=service,
        _role="ADMIN",
    )

    assert result == ["record-1", "record-2"]

    service.resolve_correlation_chain.assert_awaited_once_with(
        correlation_id="correlation-123",
    )
