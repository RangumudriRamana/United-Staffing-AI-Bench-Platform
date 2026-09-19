from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

from app.core.exceptions import AppException
from app.marketing.enums import (
    MarketingActivityType,
    MarketingChannel,
    MarketingOutcome,
)
from app.marketing.service import MarketingActivityService
from app.tasks.enums import TaskType


def make_service():
    db = MagicMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()

    service = MarketingActivityService(db)

    service.repository = MagicMock()
    service.repository.create = AsyncMock()
    service.repository.get_by_public_id = AsyncMock()
    service.repository.list_by_consultant = AsyncMock()

    return service, db


def make_consultant():
    return SimpleNamespace(
        id=10,
        public_id=UUID("11111111-1111-1111-1111-111111111111"),
        first_name="John",
        last_name="Doe",
    )


def make_vendor():
    return SimpleNamespace(
        id=20,
        public_id=UUID("22222222-2222-2222-2222-222222222222"),
    )


def make_contact(vendor_id=20):
    return SimpleNamespace(
        id=30,
        public_id=UUID("33333333-3333-3333-3333-333333333333"),
        vendor_id=vendor_id,
        last_contacted=None,
    )


def make_client(vendor_id=20):
    return SimpleNamespace(
        id=40,
        public_id=UUID("44444444-4444-4444-4444-444444444444"),
        vendor_id=vendor_id,
    )


def make_payload(
    *,
    vendor_contact_public_id=None,
    client_public_id=None,
    follow_up_required=False,
    occurred_at=None,
):
    return SimpleNamespace(
        consultant_public_id=UUID("11111111-1111-1111-1111-111111111111"),
        vendor_public_id=UUID("22222222-2222-2222-2222-222222222222"),
        vendor_contact_public_id=vendor_contact_public_id,
        client_public_id=client_public_id,
        activity_type=MarketingActivityType.PROFILE_MARKETING,
        channel=MarketingChannel.EMAIL,
        outcome=MarketingOutcome.SENT,
        subject="Test marketing activity",
        notes="Test notes",
        follow_up_required=follow_up_required,
        occurred_at=occurred_at,
    )


def make_activity():
    return SimpleNamespace(
        public_id=UUID("55555555-5555-5555-5555-555555555555"),
    )


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_consultant_or_raise_success():
    service, db = make_service()

    consultant = make_consultant()

    result = MagicMock()
    result.scalars.return_value.first.return_value = consultant
    db.execute.return_value = result

    found = await service._get_consultant_or_raise(consultant.public_id)

    assert found is consultant
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_consultant_or_raise_not_found():
    service, db = make_service()

    result = MagicMock()
    result.scalars.return_value.first.return_value = None
    db.execute.return_value = result

    with pytest.raises(AppException) as exc:
        await service._get_consultant_or_raise(
            UUID("11111111-1111-1111-1111-111111111111")
        )

    assert exc.value.status_code == 404
    assert exc.value.message == "Consultant record not found."


@pytest.mark.asyncio
async def test_get_vendor_or_raise_not_found():
    service, db = make_service()

    result = MagicMock()
    result.scalars.return_value.first.return_value = None
    db.execute.return_value = result

    with pytest.raises(AppException) as exc:
        await service._get_vendor_or_raise(
            UUID("22222222-2222-2222-2222-222222222222")
        )

    assert exc.value.status_code == 404
    assert exc.value.message == "Vendor record not found."


@pytest.mark.asyncio
async def test_get_vendor_contact_or_raise_not_found():
    service, db = make_service()

    result = MagicMock()
    result.scalars.return_value.first.return_value = None
    db.execute.return_value = result

    with pytest.raises(AppException) as exc:
        await service._get_vendor_contact_or_raise(
            UUID("33333333-3333-3333-3333-333333333333")
        )

    assert exc.value.status_code == 404
    assert exc.value.message == "Vendor contact record not found."


@pytest.mark.asyncio
async def test_get_client_or_raise_not_found():
    service, db = make_service()

    result = MagicMock()
    result.scalars.return_value.first.return_value = None
    db.execute.return_value = result

    with pytest.raises(AppException) as exc:
        await service._get_client_or_raise(
            UUID("44444444-4444-4444-4444-444444444444")
        )

    assert exc.value.status_code == 404
    assert exc.value.message == "Client record not found."


# ---------------------------------------------------------------------------
# Follow-up task type resolution
# ---------------------------------------------------------------------------


def test_resolve_follow_up_task_type_client_takes_precedence():
    result = MarketingActivityService._resolve_follow_up_task_type(
        activity_type=MarketingActivityType.CLIENT_OUTREACH,
        vendor_contact_id=30,
        client_id=40,
    )

    assert result == TaskType.FOLLOW_UP_CLIENT


def test_resolve_follow_up_task_type_vendor_contact():
    result = MarketingActivityService._resolve_follow_up_task_type(
        activity_type=MarketingActivityType.PROFILE_MARKETING,
        vendor_contact_id=30,
        client_id=None,
    )

    assert result == TaskType.FOLLOW_UP_VENDOR


def test_resolve_follow_up_task_type_consultant():
    result = MarketingActivityService._resolve_follow_up_task_type(
        activity_type=MarketingActivityType.PROFILE_MARKETING,
        vendor_contact_id=None,
        client_id=None,
    )

    assert result == TaskType.FOLLOW_UP_CONSULTANT


# ---------------------------------------------------------------------------
# create_activity
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_activity_without_follow_up():
    service, db = make_service()

    consultant = make_consultant()
    vendor = make_vendor()
    activity = make_activity()

    service._get_consultant_or_raise = AsyncMock(return_value=consultant)
    service._get_vendor_or_raise = AsyncMock(return_value=vendor)

    service.repository.create.return_value = activity
    service.repository.get_by_public_id.return_value = activity

    payload = make_payload(follow_up_required=False)

    result = await service.create_activity(
        payload=payload,
        current_user_id=99,
    )

    assert result is activity
    service.repository.create.assert_awaited_once()

    kwargs = service.repository.create.call_args.kwargs

    assert kwargs["consultant_id"] == consultant.id
    assert kwargs["vendor_id"] == vendor.id
    assert kwargs["vendor_contact_id"] is None
    assert kwargs["client_id"] is None
    assert kwargs["performed_by"] == 99

    db.add.assert_not_called()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_activity_with_vendor_contact_creates_vendor_follow_up():
    service, db = make_service()

    consultant = make_consultant()
    vendor = make_vendor()
    contact = make_contact()
    activity = make_activity()

    service._get_consultant_or_raise = AsyncMock(return_value=consultant)
    service._get_vendor_or_raise = AsyncMock(return_value=vendor)
    service._get_vendor_contact_or_raise = AsyncMock(return_value=contact)

    service.repository.create.return_value = activity
    service.repository.get_by_public_id.return_value = activity

    payload = make_payload(
        vendor_contact_public_id=contact.public_id,
        follow_up_required=True,
    )

    with patch("app.marketing.service.Task") as task_cls:
        result = await service.create_activity(
            payload=payload,
            current_user_id=99,
        )

    assert result is activity
    assert contact.last_contacted is not None

    task_cls.assert_called_once()

    task_kwargs = task_cls.call_args.kwargs

    assert task_kwargs["owner_id"] == 99
    assert task_kwargs["task_type"] == TaskType.FOLLOW_UP_VENDOR
    assert task_kwargs["related_entity_type"] == "CONSULTANT"
    assert task_kwargs["related_entity_id"] == consultant.id

    db.add.assert_called_once()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_activity_with_client_creates_client_follow_up():
    service, db = make_service()

    consultant = make_consultant()
    vendor = make_vendor()
    client = make_client()
    activity = make_activity()

    service._get_consultant_or_raise = AsyncMock(return_value=consultant)
    service._get_vendor_or_raise = AsyncMock(return_value=vendor)
    service._get_client_or_raise = AsyncMock(return_value=client)

    service.repository.create.return_value = activity
    service.repository.get_by_public_id.return_value = activity

    payload = make_payload(
        client_public_id=client.public_id,
        follow_up_required=True,
    )

    with patch("app.marketing.service.Task") as task_cls:
        result = await service.create_activity(
            payload=payload,
            current_user_id=99,
        )

    assert result is activity

    task_kwargs = task_cls.call_args.kwargs
    assert task_kwargs["task_type"] == TaskType.FOLLOW_UP_CLIENT

    db.add.assert_called_once()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_activity_uses_naive_occurred_at_when_timezone_aware():
    service, db = make_service()

    consultant = make_consultant()
    vendor = make_vendor()
    activity = make_activity()

    service._get_consultant_or_raise = AsyncMock(return_value=consultant)
    service._get_vendor_or_raise = AsyncMock(return_value=vendor)

    service.repository.create.return_value = activity
    service.repository.get_by_public_id.return_value = activity

    aware_time = datetime(
        2026,
        9,
        18,
        10,
        30,
        tzinfo=timezone.utc,
    )

    payload = make_payload(
        occurred_at=aware_time,
        follow_up_required=False,
    )

    await service.create_activity(
        payload=payload,
        current_user_id=99,
    )

    occurred_at = service.repository.create.call_args.kwargs["occurred_at"]

    assert occurred_at == datetime(2026, 9, 18, 10, 30)
    assert occurred_at.tzinfo is None


@pytest.mark.asyncio
async def test_create_activity_rejects_contact_from_different_vendor():
    service, db = make_service()

    consultant = make_consultant()
    vendor = make_vendor()
    contact = make_contact(vendor_id=999)

    service._get_consultant_or_raise = AsyncMock(return_value=consultant)
    service._get_vendor_or_raise = AsyncMock(return_value=vendor)
    service._get_vendor_contact_or_raise = AsyncMock(return_value=contact)

    payload = make_payload(
        vendor_contact_public_id=contact.public_id,
    )

    with pytest.raises(AppException) as exc:
        await service.create_activity(
            payload=payload,
            current_user_id=99,
        )

    assert exc.value.status_code == 400
    assert (
        exc.value.message
        == "Vendor contact does not belong to the selected vendor."
    )

    service.repository.create.assert_not_awaited()
    db.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_activity_rejects_client_from_different_vendor():
    service, db = make_service()

    consultant = make_consultant()
    vendor = make_vendor()
    client = make_client(vendor_id=999)

    service._get_consultant_or_raise = AsyncMock(return_value=consultant)
    service._get_vendor_or_raise = AsyncMock(return_value=vendor)
    service._get_client_or_raise = AsyncMock(return_value=client)

    payload = make_payload(
        client_public_id=client.public_id,
    )

    with pytest.raises(AppException) as exc:
        await service.create_activity(
            payload=payload,
            current_user_id=99,
        )

    assert exc.value.status_code == 400
    assert exc.value.message == "Client does not belong to the selected vendor."

    service.repository.create.assert_not_awaited()
    db.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_activity_rolls_back_on_app_exception():
    service, db = make_service()

    consultant = make_consultant()
    vendor = make_vendor()
    activity = make_activity()

    service._get_consultant_or_raise = AsyncMock(return_value=consultant)
    service._get_vendor_or_raise = AsyncMock(return_value=vendor)

    service.repository.create.side_effect = AppException(
        status_code=400,
        message="creation failed",
    )

    payload = make_payload()

    with pytest.raises(AppException) as exc:
        await service.create_activity(
            payload=payload,
            current_user_id=99,
        )

    assert exc.value.status_code == 400
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_activity_rolls_back_on_generic_exception():
    service, db = make_service()

    consultant = make_consultant()
    vendor = make_vendor()

    service._get_consultant_or_raise = AsyncMock(return_value=consultant)
    service._get_vendor_or_raise = AsyncMock(return_value=vendor)

    service.repository.create.side_effect = RuntimeError(
        "database failure"
    )

    payload = make_payload()

    with pytest.raises(RuntimeError, match="database failure"):
        await service.create_activity(
            payload=payload,
            current_user_id=99,
        )

    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_activity_reload_failure():
    service, db = make_service()

    consultant = make_consultant()
    vendor = make_vendor()
    activity = make_activity()

    service._get_consultant_or_raise = AsyncMock(return_value=consultant)
    service._get_vendor_or_raise = AsyncMock(return_value=vendor)

    service.repository.create.return_value = activity
    service.repository.get_by_public_id.return_value = None

    payload = make_payload()

    with pytest.raises(AppException) as exc:
        await service.create_activity(
            payload=payload,
            current_user_id=99,
        )

    assert exc.value.status_code == 500
    assert (
        exc.value.message
        == "Marketing activity was created but could not be reloaded."
    )

    db.rollback.assert_awaited_once()


# ---------------------------------------------------------------------------
# get_activity
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_activity_success():
    service, _ = make_service()

    activity = make_activity()
    service.repository.get_by_public_id.return_value = activity

    result = await service.get_activity(activity.public_id)

    assert result is activity


@pytest.mark.asyncio
async def test_get_activity_not_found():
    service, _ = make_service()

    service.repository.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc:
        await service.get_activity(
            UUID("55555555-5555-5555-5555-555555555555")
        )

    assert exc.value.status_code == 404
    assert exc.value.message == "Marketing activity record not found."


# ---------------------------------------------------------------------------
# list_consultant_activities
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_consultant_activities_success():
    service, _ = make_service()

    consultant = make_consultant()
    activities = [make_activity(), make_activity()]

    service._get_consultant_or_raise = AsyncMock(return_value=consultant)
    service.repository.list_by_consultant.return_value = activities

    result = await service.list_consultant_activities(
        consultant.public_id
    )

    assert result == activities
    service.repository.list_by_consultant.assert_awaited_once_with(
        consultant.id
    )


@pytest.mark.asyncio
async def test_list_consultant_activities_consultant_not_found():
    service, _ = make_service()

    service._get_consultant_or_raise = AsyncMock(
        side_effect=AppException(
            status_code=404,
            message="Consultant record not found.",
        )
    )

    with pytest.raises(AppException) as exc:
        await service.list_consultant_activities(
            UUID("11111111-1111-1111-1111-111111111111")
        )

    assert exc.value.status_code == 404
    service.repository.list_by_consultant.assert_not_awaited()