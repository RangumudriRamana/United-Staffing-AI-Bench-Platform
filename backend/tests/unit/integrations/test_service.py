from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.exceptions import AppException
from app.integrations.enums import IntegrationStatus
from app.integrations.service import IntegrationHubService


def make_service():
    db = MagicMock()
    db.commit = AsyncMock()
    db.add = MagicMock()
    db.execute = AsyncMock()
    return db, IntegrationHubService(db)


@pytest.mark.asyncio
async def test_register_connection_profile():
    db, service = make_service()

    payload = SimpleNamespace(
        provider_name="  Salesforce  ",
        integration_type="CRM",
        configuration_json={"region": "us-east"},
        credentials_reference="secret-ref-1",
    )

    result = await service.register_connection_profile(payload)

    db.add.assert_called_once()
    db.commit.assert_awaited_once()

    assert result.provider_name == "SALESFORCE"
    assert result.integration_type == "CRM"
    assert result.configuration_json == {"region": "us-east"}
    assert result.credentials_reference == "secret-ref-1"
    assert result.status == IntegrationStatus.CONNECTED
    assert result.is_enabled is True


@pytest.mark.asyncio
async def test_register_connection_profile_normalizes_provider_name():
    db, service = make_service()

    payload = SimpleNamespace(
        provider_name="  microsoft azure  ",
        integration_type="CLOUD",
        configuration_json={},
        credentials_reference=None,
    )

    result = await service.register_connection_profile(payload)

    assert result.provider_name == "MICROSOFT AZURE"


@pytest.mark.asyncio
async def test_execute_connectivity_check_success():
    db, service = make_service()

    public_id = uuid4()
    connection = SimpleNamespace(
        public_id=public_id,
        provider_name="SALESFORCE",
        status=IntegrationStatus.CONNECTED,
        last_sync_at=None,
    )

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.first.return_value = connection
    db.execute.return_value = result_proxy

    result = await service.execute_connectivity_check(public_id)

    assert result.provider_name == "SALESFORCE"
    assert result.status == IntegrationStatus.CONNECTED
    assert result.is_operational is True
    assert result.latency_ms == 45
    assert connection.last_sync_at is not None
    assert connection.last_sync_at.tzinfo is not None
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_execute_connectivity_check_not_found():
    db, service = make_service()

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.first.return_value = None
    db.execute.return_value = result_proxy

    with pytest.raises(AppException) as exc_info:
        await service.execute_connectivity_check(uuid4())

    assert exc_info.value.status_code == 404
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_connectivity_check_non_connected():
    db, service = make_service()

    connection = SimpleNamespace(
        public_id=uuid4(),
        provider_name="JIRA",
        status=IntegrationStatus.DISCONNECTED,
        last_sync_at=None,
    )

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.first.return_value = connection
    db.execute.return_value = result_proxy

    result = await service.execute_connectivity_check(connection.public_id)

    assert result.provider_name == "JIRA"
    assert result.status == IntegrationStatus.DISCONNECTED
    assert result.is_operational is False
    assert result.latency_ms == 45
    assert connection.last_sync_at is not None
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_active_connections_list():
    db, service = make_service()

    connections = [
        SimpleNamespace(provider_name="SALESFORCE", is_enabled=True),
        SimpleNamespace(provider_name="JIRA", is_enabled=True),
    ]

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.all.return_value = connections
    db.execute.return_value = result_proxy

    result = await service.fetch_active_connections_list()

    assert result == connections
    assert len(result) == 2
    assert all(connection.is_enabled for connection in result)


@pytest.mark.asyncio
async def test_fetch_active_connections_list_empty():
    db, service = make_service()

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.all.return_value = []
    db.execute.return_value = result_proxy

    result = await service.fetch_active_connections_list()

    assert result == []