from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import AppException
from app.vendors.enums import (
    ClientStatus,
    VendorStatus,
    VendorTier,
    VendorType,
)
from app.vendors.schemas import (
    ClientCreateRequest,
    ClientUpdateRequest,
    ClientFilters,
    VendorCreateRequest,
    VendorUpdateRequest,
    VendorFilters,
)
from app.shared.schemas import PaginationParams, SortParams
from app.vendors.service import VendorService


def make_service():
    db = MagicMock()
    service = VendorService(db)

    service.vendor_repo = MagicMock()
    service.client_repo = MagicMock()
    service.audit_service = MagicMock()

    service.vendor_repo.get_by_public_id = AsyncMock()
    service.vendor_repo.exists_duplicate_name = AsyncMock()
    service.vendor_repo.list_vendors_paginated = AsyncMock()

    service.client_repo.get_by_public_id = AsyncMock()
    service.client_repo.exists_duplicate_under_vendor = AsyncMock()
    service.client_repo.list_clients_paginated = AsyncMock()

    service.audit_service.write_audit_entry = AsyncMock()
    service.audit_service.get_next_entity_version = AsyncMock(return_value=1)

    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()

    return service, db


def make_vendor():
    vendor = MagicMock()
    vendor.id = 1
    vendor.public_id = uuid4()
    vendor.name = "Acme Vendor"
    vendor.vendor_type = VendorType.PRIME_VENDOR
    vendor.tier = VendorTier.TIER_2
    vendor.status = VendorStatus.ACTIVE
    vendor.website = "https://acme.example"
    vendor.preferred = False
    vendor.notes = None
    vendor.contacts = []
    return vendor


def make_client():
    client = MagicMock()
    client.id = 2
    client.public_id = uuid4()
    client.vendor_id = 1
    client.name = "Acme Client"
    client.status = ClientStatus.ACTIVE
    client.notes = None
    return client


# ============================================================
# Helpers
# ============================================================

def test_normalize_name():
    assert (
        VendorService._normalize_name(
            "  united   staffing associates  "
        )
        == "United Staffing Associates"
    )


def test_normalize_optional():
    assert VendorService._normalize_optional("  hello  ") == "hello"
    assert VendorService._normalize_optional("   ") is None
    assert VendorService._normalize_optional(None) is None


def test_normalize_email():
    assert (
        VendorService._normalize_email("  TEST@Example.COM ")
        == "test@example.com"
    )


def test_normalize_client_payload():
    data = VendorService._normalize_client_payload(
        {
            "name": "  acme   client ",
            "display_name": "  ACME  ",
            "industry": "  Technology ",
            "website": "  https://acme.com ",
            "primary_location": "  New York ",
            "notes": "  Important ",
        }
    )

    assert data["name"] == "Acme Client"
    assert data["display_name"] == "ACME"
    assert data["industry"] == "Technology"
    assert data["website"] == "https://acme.com"
    assert data["primary_location"] == "New York"
    assert data["notes"] == "Important"


def test_normalize_client_payload_missing_fields():
    data = VendorService._normalize_client_payload(
        {"name": "Acme Client"}
    )

    assert data == {"name": "Acme Client"}


def test_vendor_audit_snapshot():
    vendor = make_vendor()

    snapshot = VendorService._vendor_audit_snapshot(vendor)

    assert snapshot["public_id"] == str(vendor.public_id)
    assert snapshot["name"] == vendor.name
    assert snapshot["vendor_type"] == vendor.vendor_type.value
    assert snapshot["tier"] == vendor.tier.value
    assert snapshot["status"] == vendor.status.value
    assert snapshot["website"] == vendor.website
    assert snapshot["preferred"] is False
    assert snapshot["notes"] is None


def test_client_audit_snapshot():
    client = make_client()

    snapshot = VendorService(MagicMock())._client_audit_snapshot(client)

    assert snapshot["public_id"] == str(client.public_id)
    assert snapshot["vendor_id"] == 1
    assert snapshot["name"] == "Acme Client"
    assert snapshot["status"] == ClientStatus.ACTIVE.value
    assert snapshot["notes"] is None


def test_apply_vendor_updates():
    vendor = make_vendor()

    VendorService._apply_vendor_updates(
        vendor,
        {
            "name": "Updated Vendor",
            "preferred": True,
        },
    )

    assert vendor.name == "Updated Vendor"
    assert vendor.preferred is True


@pytest.mark.asyncio
async def test_get_vendor_or_raise_success():
    service, _ = make_service()
    vendor = make_vendor()

    service.vendor_repo.get_by_public_id.return_value = vendor

    result = await service._get_vendor_or_raise(
        vendor.public_id,
        eager_load_contacts=True,
    )

    assert result is vendor
    service.vendor_repo.get_by_public_id.assert_awaited_once_with(
        public_id=vendor.public_id,
        eager_load_contacts=True,
    )


@pytest.mark.asyncio
async def test_get_vendor_or_raise_not_found():
    service, _ = make_service()

    service.vendor_repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc:
        await service._get_vendor_or_raise(uuid4())

    assert exc.value.status_code == 404
    assert exc.value.message == "Vendor record not found."


@pytest.mark.asyncio
async def test_get_client_or_raise_success():
    service, _ = make_service()
    client = make_client()

    service.client_repo.get_by_public_id.return_value = client

    result = await service._get_client_or_raise(
        client.public_id,
        eager_load_vendor=True,
    )

    assert result is client
    service.client_repo.get_by_public_id.assert_awaited_once_with(
        public_id=client.public_id,
        eager_load_vendor=True,
    )


@pytest.mark.asyncio
async def test_get_client_or_raise_not_found():
    service, _ = make_service()

    service.client_repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc:
        await service._get_client_or_raise(uuid4())

    assert exc.value.status_code == 404
    assert exc.value.message == "Client record not found."


@pytest.mark.asyncio
async def test_ensure_unique_vendor_name_success():
    service, _ = make_service()

    service.vendor_repo.exists_duplicate_name.return_value = False

    result = await service._ensure_unique_vendor_name(
        "Acme Vendor"
    )

    assert result is None


@pytest.mark.asyncio
async def test_ensure_unique_vendor_name_duplicate():
    service, _ = make_service()

    service.vendor_repo.exists_duplicate_name.return_value = True

    with pytest.raises(AppException) as exc:
        await service._ensure_unique_vendor_name("Acme Vendor")

    assert exc.value.status_code == 400
    assert exc.value.message == "Vendor name already exists."


# ============================================================
# Vendor CRUD
# ============================================================

@pytest.mark.asyncio
async def test_create_vendor_success_without_contacts():
    service, db = make_service()

    service.vendor_repo.exists_duplicate_name.return_value = False

    vendor = make_vendor()
    service.vendor_repo.create.return_value = vendor
    service.vendor_repo.get_by_public_id.return_value = vendor

    payload = VendorCreateRequest(
        name="  acme   vendor ",
        vendor_type=VendorType.PRIME_VENDOR,
        tier=VendorTier.TIER_2,
        status=VendorStatus.ACTIVE,
        website="  https://acme.com  ",
        preferred=False,
        notes="  Test vendor  ",
        contacts=[],
    )

    result = await service.create_vendor(
        payload,
        current_user_id=10,
    )

    assert result is vendor
    service.vendor_repo.create.assert_called_once()

    create_kwargs = service.vendor_repo.create.call_args.kwargs
    assert create_kwargs["name"] == "Acme Vendor"
    assert create_kwargs["website"] == "https://acme.com"
    assert create_kwargs["notes"] == "Test vendor"
    assert create_kwargs["created_by"] == 10

    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_vendor_with_contact_normalizes_contact():
    service, db = make_service()

    service.vendor_repo.exists_duplicate_name.return_value = False

    vendor = make_vendor()
    service.vendor_repo.create.return_value = vendor
    service.vendor_repo.get_by_public_id.return_value = vendor

    payload = VendorCreateRequest(
        name="Acme Vendor",
        contacts=[
            {
                "name": "  John Doe ",
                "email": "  JOHN@EXAMPLE.COM ",
                "title": "  Recruiter ",
                "phone": " 123456 ",
                "linkedin": "  linkedin.com/john ",
            }
        ],
    )

    result = await service.create_vendor(
        payload,
        current_user_id=10,
    )

    assert result is vendor
    assert len(vendor.contacts) == 1
    contact = vendor.contacts[0]

    assert contact.name == "John Doe"
    assert contact.email == "john@example.com"
    assert contact.title == "Recruiter"
    assert contact.phone == "123456"
    assert contact.linkedin == "linkedin.com/john"


@pytest.mark.asyncio
async def test_create_vendor_duplicate_name():
    service, db = make_service()

    service.vendor_repo.exists_duplicate_name.return_value = True

    payload = VendorCreateRequest(
        name="Acme Vendor"
    )

    with pytest.raises(AppException) as exc:
        await service.create_vendor(
            payload,
            current_user_id=10,
        )

    assert exc.value.status_code == 400
    service.vendor_repo.create.assert_not_called()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_vendor_rolls_back_on_repository_error():
    service, db = make_service()

    service.vendor_repo.exists_duplicate_name.return_value = False
    service.vendor_repo.create.side_effect = RuntimeError("DB failure")

    payload = VendorCreateRequest(
        name="Acme Vendor"
    )

    with pytest.raises(RuntimeError):
        await service.create_vendor(
            payload,
            current_user_id=10,
        )

    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_vendor_reload_failure():
    service, db = make_service()

    service.vendor_repo.exists_duplicate_name.return_value = False

    vendor = make_vendor()
    service.vendor_repo.create.return_value = vendor
    service.vendor_repo.get_by_public_id.return_value = None

    payload = VendorCreateRequest(
        name="Acme Vendor"
    )

    with pytest.raises(AppException) as exc:
        await service.create_vendor(
            payload,
            current_user_id=10,
        )

    assert exc.value.status_code == 500
    assert "could not be reloaded" in exc.value.message
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_vendor():
    service, _ = make_service()
    vendor = make_vendor()

    service.vendor_repo.get_by_public_id.return_value = vendor

    result = await service.get_vendor(vendor.public_id)

    assert result is vendor


@pytest.mark.asyncio
async def test_list_vendors():
    service, _ = make_service()

    expected = ([], MagicMock())
    service.vendor_repo.list_vendors_paginated.return_value = expected

    result = await service.list_vendors(
        PaginationParams(),
        SortParams(),
        VendorFilters(),
    )

    assert result == expected


@pytest.mark.asyncio
async def test_update_vendor_success():
    service, db = make_service()

    vendor = make_vendor()
    service.vendor_repo.get_by_public_id.return_value = vendor
    service.vendor_repo.exists_duplicate_name.return_value = False

    payload = VendorUpdateRequest(
        name="  Updated Vendor ",
        website="  https://updated.com ",
        notes="  Updated notes ",
        preferred=True,
    )

    result = await service.update_vendor(
        vendor.public_id,
        payload,
        current_user_id=20,
    )

    assert result is vendor
    assert vendor.name == "Updated Vendor"
    assert vendor.website == "https://updated.com"
    assert vendor.notes == "Updated notes"
    assert vendor.preferred is True
    assert vendor.updated_by == 20

    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(vendor)
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_vendor_name_duplicate():
    service, db = make_service()

    vendor = make_vendor()
    service.vendor_repo.get_by_public_id.return_value = vendor
    service.vendor_repo.exists_duplicate_name.return_value = True

    payload = VendorUpdateRequest(name="Different Vendor")

    with pytest.raises(AppException) as exc:
        await service.update_vendor(
            vendor.public_id,
            payload,
            current_user_id=20,
        )

    assert exc.value.status_code == 400
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_vendor_repository_error_rolls_back():
    service, db = make_service()

    vendor = make_vendor()
    service.vendor_repo.get_by_public_id.return_value = vendor
    service.db.flush.side_effect = RuntimeError("flush failure")

    payload = VendorUpdateRequest(notes="Updated")

    with pytest.raises(RuntimeError):
        await service.update_vendor(
            vendor.public_id,
            payload,
            current_user_id=20,
        )

    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_vendor_reload_failure():
    service, db = make_service()

    vendor = make_vendor()

    service.vendor_repo.get_by_public_id.side_effect = [
        vendor,
        None,
    ]

    payload = VendorUpdateRequest(notes="Updated")

    with pytest.raises(AppException) as exc:
        await service.update_vendor(
            vendor.public_id,
            payload,
            current_user_id=20,
        )

    assert exc.value.status_code == 500
    assert "Unable to reload updated vendor." in exc.value.message
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_archive_vendor_success():
    service, db = make_service()

    vendor = make_vendor()
    service.vendor_repo.get_by_public_id.return_value = vendor

    await service.archive_vendor(
        vendor.public_id,
        current_user_id=30,
    )

    assert vendor.status == VendorStatus.INACTIVE
    assert vendor.updated_by == 30
    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_archive_vendor_error_rolls_back():
    service, db = make_service()

    vendor = make_vendor()
    service.vendor_repo.get_by_public_id.return_value = vendor
    db.flush.side_effect = RuntimeError("flush failure")

    with pytest.raises(RuntimeError):
        await service.archive_vendor(
            vendor.public_id,
            current_user_id=30,
        )

    db.rollback.assert_awaited_once()


# ============================================================
# Client CRUD
# ============================================================

@pytest.mark.asyncio
async def test_create_client_success():
    service, db = make_service()

    vendor = make_vendor()
    client = make_client()

    service.vendor_repo.get_by_public_id.return_value = vendor
    service.client_repo.exists_duplicate_under_vendor.return_value = False
    service.client_repo.create.return_value = client
    service.client_repo.get_by_public_id.return_value = client

    payload = ClientCreateRequest(
        vendor_public_id=vendor.public_id,
        name="  acme   client ",
        display_name="  ACME CLIENT ",
        industry="  Technology ",
        website="  https://client.com ",
        primary_location="  New York ",
        notes="  Important ",
    )

    result = await service.create_client(
        payload,
        current_user_id=40,
    )

    assert result is client

    create_kwargs = service.client_repo.create.call_args.kwargs
    assert create_kwargs["name"] == "Acme Client"
    assert create_kwargs["display_name"] == "ACME CLIENT"
    assert create_kwargs["industry"] == "Technology"
    assert create_kwargs["website"] == "https://client.com"
    assert create_kwargs["primary_location"] == "New York"
    assert create_kwargs["notes"] == "Important"
    assert create_kwargs["vendor_id"] == vendor.id
    assert create_kwargs["created_by"] == 40

    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_client_vendor_not_found():
    service, db = make_service()

    service.vendor_repo.get_by_public_id.return_value = None

    payload = ClientCreateRequest(
        vendor_public_id=uuid4(),
        name="Acme Client",
    )

    with pytest.raises(AppException) as exc:
        await service.create_client(
            payload,
            current_user_id=40,
        )

    assert exc.value.status_code == 404
    service.client_repo.create.assert_not_called()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_client_duplicate():
    service, db = make_service()

    vendor = make_vendor()

    service.vendor_repo.get_by_public_id.return_value = vendor
    service.client_repo.exists_duplicate_under_vendor.return_value = True

    payload = ClientCreateRequest(
        vendor_public_id=vendor.public_id,
        name="Acme Client",
    )

    with pytest.raises(AppException) as exc:
        await service.create_client(
            payload,
            current_user_id=40,
        )

    assert exc.value.status_code == 400
    service.client_repo.create.assert_not_called()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_client_reload_failure():
    service, db = make_service()

    vendor = make_vendor()
    client = make_client()

    service.vendor_repo.get_by_public_id.return_value = vendor
    service.client_repo.exists_duplicate_under_vendor.return_value = False
    service.client_repo.create.return_value = client
    service.client_repo.get_by_public_id.return_value = None

    payload = ClientCreateRequest(
        vendor_public_id=vendor.public_id,
        name="Acme Client",
    )

    with pytest.raises(AppException) as exc:
        await service.create_client(
            payload,
            current_user_id=40,
        )

    assert exc.value.status_code == 500
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_client_error_rolls_back():
    service, db = make_service()

    vendor = make_vendor()

    service.vendor_repo.get_by_public_id.return_value = vendor
    service.client_repo.exists_duplicate_under_vendor.return_value = False
    service.client_repo.create.side_effect = RuntimeError("DB failure")

    payload = ClientCreateRequest(
        vendor_public_id=vendor.public_id,
        name="Acme Client",
    )

    with pytest.raises(RuntimeError):
        await service.create_client(
            payload,
            current_user_id=40,
        )

    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_client():
    service, _ = make_service()
    client = make_client()

    service.client_repo.get_by_public_id.return_value = client

    result = await service.get_client(client.public_id)

    assert result is client


@pytest.mark.asyncio
async def test_list_clients():
    service, _ = make_service()

    expected = ([], MagicMock())
    service.client_repo.list_clients_paginated.return_value = expected

    result = await service.list_clients(
        PaginationParams(),
        SortParams(),
        ClientFilters(),
    )

    assert result == expected


@pytest.mark.asyncio
async def test_update_client_success():
    service, db = make_service()

    client = make_client()
    service.client_repo.get_by_public_id.return_value = client
    service.client_repo.exists_duplicate_under_vendor.return_value = False

    payload = ClientUpdateRequest(
        name="  Updated Client ",
        industry="  Finance ",
        preferred=True,
    )

    result = await service.update_client(
        client.public_id,
        payload,
        current_user_id=50,
    )

    assert result is client
    assert client.name == "Updated Client"
    assert client.industry == "Finance"
    assert client.preferred is True
    assert client.updated_by == 50

    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(client)
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_client_name_duplicate():
    service, db = make_service()

    client = make_client()
    service.client_repo.get_by_public_id.return_value = client
    service.client_repo.exists_duplicate_under_vendor.return_value = True

    payload = ClientUpdateRequest(name="Different Client")

    with pytest.raises(AppException) as exc:
        await service.update_client(
            client.public_id,
            payload,
            current_user_id=50,
        )

    assert exc.value.status_code == 400
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_client_same_name_skips_duplicate_check():
    service, db = make_service()

    client = make_client()
    service.client_repo.get_by_public_id.return_value = client

    payload = ClientUpdateRequest(name="  acme   client ")

    result = await service.update_client(
        client.public_id,
        payload,
        current_user_id=50,
    )

    assert result is client
    service.client_repo.exists_duplicate_under_vendor.assert_not_awaited()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_client_error_rolls_back():
    service, db = make_service()

    client = make_client()
    service.client_repo.get_by_public_id.return_value = client
    db.flush.side_effect = RuntimeError("flush failure")

    payload = ClientUpdateRequest(notes="Updated")

    with pytest.raises(RuntimeError):
        await service.update_client(
            client.public_id,
            payload,
            current_user_id=50,
        )

    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_client_reload_failure():
    service, db = make_service()

    client = make_client()

    service.client_repo.get_by_public_id.side_effect = [
        client,
        None,
    ]

    payload = ClientUpdateRequest(notes="Updated")

    with pytest.raises(AppException) as exc:
        await service.update_client(
            client.public_id,
            payload,
            current_user_id=50,
        )

    assert exc.value.status_code == 500
    assert "Unable to reload updated client." in exc.value.message
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_archive_client_success():
    service, db = make_service()

    client = make_client()
    service.client_repo.get_by_public_id.return_value = client

    await service.archive_client(
        client.public_id,
        current_user_id=60,
    )

    assert client.status == ClientStatus.INACTIVE
    assert client.updated_by == 60
    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_archive_client_error_rolls_back():
    service, db = make_service()

    client = make_client()
    service.client_repo.get_by_public_id.return_value = client
    db.flush.side_effect = RuntimeError("flush failure")

    with pytest.raises(RuntimeError):
        await service.archive_client(
            client.public_id,
            current_user_id=60,
        )

    db.rollback.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_vendor_same_name_skips_duplicate_check():
    service, db = make_service()

    vendor = make_vendor()
    service.vendor_repo.get_by_public_id.return_value = vendor

    payload = VendorUpdateRequest(
        name="  acme   vendor ",
        website="  https://updated.com ",
        notes="  Updated notes ",
    )

    result = await service.update_vendor(
        vendor.public_id,
        payload,
        current_user_id=20,
    )

    assert result is vendor
    assert vendor.name == "Acme Vendor"
    assert vendor.website == "https://updated.com"
    assert vendor.notes == "Updated notes"
    service.vendor_repo.exists_duplicate_name.assert_not_awaited()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_vendor_without_notes_preserves_notes():
    service, db = make_service()

    vendor = make_vendor()
    vendor.notes = "Existing notes"
    service.vendor_repo.get_by_public_id.return_value = vendor

    payload = VendorUpdateRequest(
        website="  https://updated.com ",
    )

    result = await service.update_vendor(
        vendor.public_id,
        payload,
        current_user_id=20,
    )

    assert result is vendor
    assert vendor.website == "https://updated.com"
    assert vendor.notes == "Existing notes"
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_archive_vendor_app_exception_rolls_back():
    service, db = make_service()

    vendor = make_vendor()
    service.vendor_repo.get_by_public_id.return_value = vendor

    service.audit_service.get_next_entity_version.side_effect = AppException(
        status_code=400,
        message="Audit failure",
    )

    with pytest.raises(AppException) as exc:
        await service.archive_vendor(
            vendor.public_id,
            current_user_id=30,
        )

    assert exc.value.status_code == 400
    assert exc.value.message == "Audit failure"
    db.rollback.assert_awaited_once()