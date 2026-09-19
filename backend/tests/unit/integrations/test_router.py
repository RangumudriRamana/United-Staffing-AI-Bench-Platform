from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.integrations.router import (
    create_external_provider_connection,
    trigger_connection_ping_test,
    list_active_integration_connections,
)


@pytest.mark.asyncio
async def test_create_external_provider_connection():
    payload = SimpleNamespace(provider_name="Salesforce")
    expected = {"public_id": "integration-1"}

    service = SimpleNamespace(
        register_connection_profile=AsyncMock(return_value=expected)
    )

    result = await create_external_provider_connection(
        payload=payload,
        service=service,
        _role=None,
    )

    assert result == expected
    service.register_connection_profile.assert_awaited_once_with(
        payload=payload
    )


@pytest.mark.asyncio
async def test_trigger_connection_ping_test():
    public_id = uuid4()
    expected = {
        "provider_name": "SALESFORCE",
        "is_operational": True,
        "latency_ms": 45,
    }

    service = SimpleNamespace(
        execute_connectivity_check=AsyncMock(return_value=expected)
    )

    result = await trigger_connection_ping_test(
        public_id=public_id,
        service=service,
        _role=None,
    )

    assert result == expected
    service.execute_connectivity_check.assert_awaited_once_with(
        public_id=public_id
    )


@pytest.mark.asyncio
async def test_list_active_integration_connections():
    expected = [
        {"public_id": "integration-1"},
        {"public_id": "integration-2"},
    ]

    service = SimpleNamespace(
        fetch_active_connections_list=AsyncMock(return_value=expected)
    )

    result = await list_active_integration_connections(
        service=service,
        _role=None,
    )

    assert result == expected
    service.fetch_active_connections_list.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_trigger_connection_ping_test_propagates_error():
    public_id = uuid4()

    service = SimpleNamespace(
        execute_connectivity_check=AsyncMock(
            side_effect=ValueError("connection failed")
        )
    )

    with pytest.raises(ValueError, match="connection failed"):
        await trigger_connection_ping_test(
            public_id=public_id,
            service=service,
            _role=None,
        )