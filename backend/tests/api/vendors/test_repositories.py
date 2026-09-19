from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.vendors.enums import (
    ClientStatus,
    VendorStatus,
    VendorTier,
    VendorType,
)
from app.vendors.repositories import VendorRepository, ClientRepository
from app.vendors.schemas import VendorFilters, ClientFilters
from app.shared.schemas import PaginationParams, SortParams


def mock_db():
    return MagicMock()


# ============================================================
# VendorRepository
# ============================================================

def test_vendor_create():
    db = mock_db()
    repo = VendorRepository(db)

    vendor = repo.create(name="Test Vendor")

    assert vendor.name == "Test Vendor"
    db.add.assert_called_once_with(vendor)


@pytest.mark.asyncio
async def test_vendor_get_by_public_id():
    db = mock_db()
    repo = VendorRepository(db)

    expected = MagicMock()
    result = MagicMock()
    result.scalars.return_value.first.return_value = expected
    db.execute = AsyncMock(return_value=result)

    public_id = uuid4()

    actual = await repo.get_by_public_id(public_id)

    assert actual is expected
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_vendor_get_by_public_id_with_eager_loading():
    db = mock_db()
    repo = VendorRepository(db)

    expected = MagicMock()
    result = MagicMock()
    result.scalars.return_value.first.return_value = expected
    db.execute = AsyncMock(return_value=result)

    actual = await repo.get_by_public_id(
        uuid4(),
        eager_load_contacts=True,
    )

    assert actual is expected
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_vendor_get_by_public_id_not_found():
    db = mock_db()
    repo = VendorRepository(db)

    result = MagicMock()
    result.scalars.return_value.first.return_value = None
    db.execute = AsyncMock(return_value=result)

    actual = await repo.get_by_public_id(uuid4())

    assert actual is None


@pytest.mark.asyncio
async def test_vendor_duplicate_name():
    db = mock_db()
    repo = VendorRepository(db)

    result = MagicMock()
    result.scalar.return_value = True
    db.execute = AsyncMock(return_value=result)

    assert await repo.exists_duplicate_name("  Acme  ") is True


@pytest.mark.asyncio
async def test_vendor_duplicate_name_with_exclude():
    db = mock_db()
    repo = VendorRepository(db)

    result = MagicMock()
    result.scalar.return_value = False
    db.execute = AsyncMock(return_value=result)

    assert await repo.exists_duplicate_name(
        "Acme",
        exclude_id=10,
    ) is False


@pytest.mark.asyncio
async def test_vendor_duplicate_name_not_found():
    db = mock_db()
    repo = VendorRepository(db)

    result = MagicMock()
    result.scalar.return_value = False
    db.execute = AsyncMock(return_value=result)

    assert await repo.exists_duplicate_name("New Vendor") is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filters",
    [
        VendorFilters(),
        VendorFilters(vendor_type=VendorType.PRIME_VENDOR),
        VendorFilters(tier=VendorTier.TIER_2),
        VendorFilters(status=VendorStatus.ACTIVE),
        VendorFilters(preferred_only=True),
        VendorFilters(search_text="  Acme  "),
        VendorFilters(
            vendor_type=VendorType.PRIME_VENDOR,
            tier=VendorTier.TIER_2,
            status=VendorStatus.ACTIVE,
            preferred_only=True,
            search_text="Acme",
        ),
    ],
)
async def test_vendor_list_filters(filters):
    db = mock_db()
    repo = VendorRepository(db)

    expected = {"items": [], "total": 0}

    with patch(
        "app.vendors.repositories.paginate_repository_query",
        new=AsyncMock(return_value=expected),
    ) as paginate:
        result = await repo.list_vendors_paginated(
            filters,
            PaginationParams(page=1, page_size=25),
            SortParams(),
        )

    assert result == expected
    paginate.assert_awaited_once()


# ============================================================
# ClientRepository
# ============================================================

def test_client_create():
    db = mock_db()
    repo = ClientRepository(db)

    client = repo.create(
        name="Test Client",
        vendor_id=1,
    )

    assert client.name == "Test Client"
    assert client.vendor_id == 1
    db.add.assert_called_once_with(client)


@pytest.mark.asyncio
async def test_client_get_by_public_id():
    db = mock_db()
    repo = ClientRepository(db)

    expected = MagicMock()
    result = MagicMock()
    result.scalars.return_value.first.return_value = expected
    db.execute = AsyncMock(return_value=result)

    actual = await repo.get_by_public_id(uuid4())

    assert actual is expected


@pytest.mark.asyncio
async def test_client_get_by_public_id_with_vendor():
    db = mock_db()
    repo = ClientRepository(db)

    expected = MagicMock()
    result = MagicMock()
    result.scalars.return_value.first.return_value = expected
    db.execute = AsyncMock(return_value=result)

    actual = await repo.get_by_public_id(
        uuid4(),
        eager_load_vendor=True,
    )

    assert actual is expected
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_client_get_by_public_id_not_found():
    db = mock_db()
    repo = ClientRepository(db)

    result = MagicMock()
    result.scalars.return_value.first.return_value = None
    db.execute = AsyncMock(return_value=result)

    actual = await repo.get_by_public_id(uuid4())

    assert actual is None


@pytest.mark.asyncio
async def test_client_duplicate_under_vendor():
    db = mock_db()
    repo = ClientRepository(db)

    result = MagicMock()
    result.scalar.return_value = True
    db.execute = AsyncMock(return_value=result)

    assert await repo.exists_duplicate_under_vendor(
        vendor_id=1,
        name="  Client A  ",
    ) is True


@pytest.mark.asyncio
async def test_client_duplicate_under_vendor_with_exclude():
    db = mock_db()
    repo = ClientRepository(db)

    result = MagicMock()
    result.scalar.return_value = False
    db.execute = AsyncMock(return_value=result)

    assert await repo.exists_duplicate_under_vendor(
        vendor_id=1,
        name="Client A",
        exclude_id=5,
    ) is False


@pytest.mark.asyncio
async def test_client_duplicate_under_vendor_not_found():
    db = mock_db()
    repo = ClientRepository(db)

    result = MagicMock()
    result.scalar.return_value = False
    db.execute = AsyncMock(return_value=result)

    assert await repo.exists_duplicate_under_vendor(
        vendor_id=1,
        name="New Client",
    ) is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filters",
    [
        ClientFilters(),
        ClientFilters(vendor_public_id=uuid4()),
        ClientFilters(status=ClientStatus.ACTIVE),
        ClientFilters(industry="  Technology  "),
        ClientFilters(preferred_only=True),
        ClientFilters(search_text="  Acme  "),
        ClientFilters(
            vendor_public_id=uuid4(),
            status=ClientStatus.ACTIVE,
            industry="Technology",
            preferred_only=True,
            search_text="Acme",
        ),
    ],
)
async def test_client_list_filters(filters):
    db = mock_db()
    repo = ClientRepository(db)

    expected = {"items": [], "total": 0}

    with patch(
        "app.vendors.repositories.paginate_repository_query",
        new=AsyncMock(return_value=expected),
    ) as paginate:
        result = await repo.list_clients_paginated(
            filters,
            PaginationParams(page=1, page_size=25),
            SortParams(),
        )

    assert result == expected
    paginate.assert_awaited_once()
