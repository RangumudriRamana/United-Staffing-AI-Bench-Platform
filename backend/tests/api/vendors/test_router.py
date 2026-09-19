from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.auth.enums import Role
from app.vendors.router import (
    archive_client,
    archive_vendor,
    create_client,
    create_vendor,
    get_client,
    get_vendor,
    list_clients,
    list_vendors,
    update_client,
    update_vendor,
)


def make_user():
    return SimpleNamespace(id=10)


def make_service():
    service = MagicMock()

    service.create_vendor = AsyncMock()
    service.list_vendors = AsyncMock()
    service.get_vendor = AsyncMock()
    service.update_vendor = AsyncMock()
    service.archive_vendor = AsyncMock()

    service.create_client = AsyncMock()
    service.list_clients = AsyncMock()
    service.get_client = AsyncMock()
    service.update_client = AsyncMock()
    service.archive_client = AsyncMock()

    return service


@pytest.mark.asyncio
async def test_create_vendor():
    service = make_service()
    user = make_user()
    vendor = MagicMock()

    service.create_vendor.return_value = vendor

    payload = MagicMock()

    result = await create_vendor(
        payload=payload,
        service=service,
        current_user=user,
    )

    assert result is vendor
    service.create_vendor.assert_awaited_once_with(payload, 10)


@pytest.mark.asyncio
async def test_list_vendors():
    service = make_service()
    expected_records = [MagicMock()]
    expected_metadata = MagicMock()

    service.list_vendors.return_value = (
        expected_records,
        expected_metadata,
    )

    pagination = MagicMock()
    sort = MagicMock()
    filters = MagicMock()

    result = await list_vendors(
        pagination=pagination,
        sort=sort,
        filters=filters,
        service=service,
    )

    assert result["data"] == expected_records
    assert result["pagination"] is expected_metadata
    service.list_vendors.assert_awaited_once_with(
        pagination,
        sort,
        filters,
    )


@pytest.mark.asyncio
async def test_get_vendor():
    service = make_service()
    vendor = MagicMock()
    public_id = uuid4()

    service.get_vendor.return_value = vendor

    result = await get_vendor(
        public_id=public_id,
        service=service,
    )

    assert result is vendor
    service.get_vendor.assert_awaited_once_with(public_id)


@pytest.mark.asyncio
async def test_update_vendor():
    service = make_service()
    user = make_user()
    vendor = MagicMock()
    public_id = uuid4()
    payload = MagicMock()

    service.update_vendor.return_value = vendor

    result = await update_vendor(
        public_id=public_id,
        payload=payload,
        service=service,
        current_user=user,
    )

    assert result is vendor
    service.update_vendor.assert_awaited_once_with(
        public_id,
        payload,
        10,
    )


@pytest.mark.asyncio
async def test_archive_vendor():
    service = make_service()
    user = make_user()
    public_id = uuid4()

    result = await archive_vendor(
        public_id=public_id,
        service=service,
        current_user=user,
    )

    assert result is None
    service.archive_vendor.assert_awaited_once_with(
        public_id=public_id,
        current_user_id=10,
    )


@pytest.mark.asyncio
async def test_create_client():
    service = make_service()
    user = make_user()
    client = MagicMock()

    service.create_client.return_value = client

    payload = MagicMock()

    result = await create_client(
        payload=payload,
        service=service,
        current_user=user,
    )

    assert result is client
    service.create_client.assert_awaited_once_with(payload, 10)


@pytest.mark.asyncio
async def test_list_clients():
    service = make_service()
    expected_records = [MagicMock()]
    expected_metadata = MagicMock()

    service.list_clients.return_value = (
        expected_records,
        expected_metadata,
    )

    pagination = MagicMock()
    sort = MagicMock()
    filters = MagicMock()

    result = await list_clients(
        pagination=pagination,
        sort=sort,
        filters=filters,
        service=service,
    )

    assert result["data"] == expected_records
    assert result["pagination"] is expected_metadata
    service.list_clients.assert_awaited_once_with(
        pagination,
        sort,
        filters,
    )


@pytest.mark.asyncio
async def test_get_client():
    service = make_service()
    client = MagicMock()
    public_id = uuid4()

    service.get_client.return_value = client

    result = await get_client(
        public_id=public_id,
        service=service,
    )

    assert result is client
    service.get_client.assert_awaited_once_with(public_id)


@pytest.mark.asyncio
async def test_update_client():
    service = make_service()
    user = make_user()
    client = MagicMock()
    public_id = uuid4()
    payload = MagicMock()

    service.update_client.return_value = client

    result = await update_client(
        public_id=public_id,
        payload=payload,
        service=service,
        current_user=user,
    )

    assert result is client
    service.update_client.assert_awaited_once_with(
        public_id,
        payload,
        10,
    )


@pytest.mark.asyncio
async def test_archive_client():
    service = make_service()
    user = make_user()
    public_id = uuid4()

    result = await archive_client(
        public_id=public_id,
        service=service,
        current_user=user,
    )

    assert result is None
    service.archive_client.assert_awaited_once_with(
        public_id,
        10,
    )