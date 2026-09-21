from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.integrations.router import (
    create_external_provider_connection,
    trigger_connection_ping_test,
    list_active_integration_connections,
)


@pytest.mark.asyncio
async def test_create_external_provider_connection():
    service = MagicMock()
    service.register_connection_profile = AsyncMock(
        return_value={"id": 1}
    )
    payload = MagicMock()

    result = await create_external_provider_connection(
        payload=payload,
        service=service,
        _role=MagicMock(),
    )

    assert result == {"id": 1}
    service.register_connection_profile.assert_awaited_once_with(
        payload=payload
    )


@pytest.mark.asyncio
async def test_trigger_connection_ping_test():
    service = MagicMock()
    service.execute_connectivity_check = AsyncMock(
        return_value={"healthy": True}
    )
    public_id = uuid4()

    result = await trigger_connection_ping_test(
        public_id=public_id,
        service=service,
        _role=MagicMock(),
    )

    assert result == {"healthy": True}
    service.execute_connectivity_check.assert_awaited_once_with(
        public_id=public_id
    )


@pytest.mark.asyncio
async def test_list_active_integration_connections():
    service = MagicMock()
    service.fetch_active_connections_list = AsyncMock(
        return_value=[{"id": 1}]
    )

    result = await list_active_integration_connections(
        service=service,
        _role=MagicMock(),
    )

    assert result == [{"id": 1}]
    service.fetch_active_connections_list.assert_awaited_once()