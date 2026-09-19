from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.exceptions import AppException
from app.marketing.service import MarketingActivityService
from app.tasks.enums import TaskPriority, TaskStatus, TaskType


def make_service():
    db = MagicMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.add = MagicMock()

    service = MarketingActivityService(db)
    service.repository.create = AsyncMock()
    service.repository.get_by_public_id = AsyncMock()
    service.repository.list_by_consultant = AsyncMock()

    return db, service


def scalar_result(value):
    result = MagicMock()
    result.scalars.return_value.first.return_value = value
    return result


@pytest.mark.asyncio
async def test_get_consultant_or_raise_returns_consultant():
    db, service = make_service()

    consultant = SimpleNamespace(id=10)
    db.execute.return_value = scalar_result(consultant)

    result = await service._get_consultant_or_raise(uuid4())

    assert result is consultant


@pytest.mark.asyncio
async def test_get_consultant_or_raise_not_found():
    db, service = make_service()
    db.execute.return_value = scalar_result(None)

    with pytest.raises(AppException) as exc_info:
        await service._get_consultant_or_raise(uuid4())

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_vendor_or_raise_not_found():
    db, service = make_service()
    db.execute.return_value = scalar_result(None)

    with pytest.raises(AppException) as exc_info:
        await service._get_vendor_or_raise(uuid4())

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_vendor_contact_or_raise_not_found():
    db, service = make_service()
    db.execute.return_value = scalar_result(None)

    with pytest.raises(AppException) as exc_info:
        await service._get_vendor_contact_or_raise(uuid4())

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_client_or_raise_not_found():
    db, service = make_service()
    db.execute.return_value = scalar_result(None)

    with pytest.raises(AppException) as exc_info:
        await service._get_client_or_raise(uuid4())

    assert exc_info.value.status_code == 404


def test_resolve_follow_up_task_type_client():
    result = MarketingActivityService._resolve_follow_up_task_type(
        activity_type=None,
        vendor_contact_id=20,
        client_id=30,
    )

    assert result == TaskType.FOLLOW_UP_CLIENT


def test_resolve_follow_up_task_type_vendor():
    result = MarketingActivityService._resolve_follow_up_task_type(
        activity_type=None,
        vendor_contact_id=20,
        client_id=None,
    )

    assert result == TaskType.FOLLOW_UP_VENDOR


def test_resolve_follow_up_task_type_consultant():
    result = MarketingActivityService._resolve_follow_up_task_type(
        activity_type=None,
        vendor_contact_id=None,
        client_id=None,
    )

    assert result == TaskType.FOLLOW_UP_CONSULTANT


@pytest.mark.asyncio
async def test_create_activity_success_with_follow_up_task():
    db, service = make_service()

    consultant = SimpleNamespace(
        id=10,
        first_name="John",
        last_name="Doe",
    )
    vendor = SimpleNamespace(id=20)
    contact = SimpleNamespace(id=30, vendor_id=20, last_contacted=None)
    client = SimpleNamespace(id=40, vendor_id=20)

    activity_public_id = uuid4()
    activity = SimpleNamespace(public_id=activity_public_id)

    service.repository.create.return_value = activity
    service.repository.get_by_public_id.return_value = activity

    db.execute.side_effect = [
        scalar_result(consultant),
        scalar_result(vendor),
        scalar_result(contact),
        scalar_result(client),
    ]

    occurred_at = datetime(
        2026, 1, 10, 12, 30, tzinfo=timezone.utc
    )

    payload = SimpleNamespace(
        consultant_public_id=uuid4(),
        vendor_public_id=uuid4(),
        vendor_contact_public_id=uuid4(),
        client_public_id=uuid4(),
        activity_type="CALL",
        channel="PHONE",
        outcome="CONNECTED",
        subject="Follow-up",
        notes="Discussed requirement",
        follow_up_required=True,
        occurred_at=occurred_at,
    )

    result = await service.create_activity(
        payload=payload,
        current_user_id=99,
    )

    assert result is activity
    assert contact.last_contacted == occurred_at.replace(tzinfo=None)

    service.repository.create.assert_awaited_once()
    db.add.assert_called_once()

    task = db.add.call_args.args[0]

    assert task.owner_id == 99
    assert task.task_type == TaskType.FOLLOW_UP_CLIENT
    assert task.priority == TaskPriority.NORMAL
    assert task.status == TaskStatus.OPEN
    assert task.related_entity_type == "CONSULTANT"
    assert task.related_entity_id == 10
    assert task.due_at == occurred_at.replace(tzinfo=None)

    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_activity_success_without_follow_up():
    db, service = make_service()

    consultant = SimpleNamespace(
        id=10,
        first_name="John",
        last_name="Doe",
    )
    vendor = SimpleNamespace(id=20)
    activity = SimpleNamespace(public_id=uuid4())

    service.repository.create.return_value = activity
    service.repository.get_by_public_id.return_value = activity

    db.execute.side_effect = [
        scalar_result(consultant),
        scalar_result(vendor),
    ]

    payload = SimpleNamespace(
        consultant_public_id=uuid4(),
        vendor_public_id=uuid4(),
        vendor_contact_public_id=None,
        client_public_id=None,
        activity_type="EMAIL",
        channel="EMAIL",
        outcome="SENT",
        subject="Email",
        notes="Sent profile",
        follow_up_required=False,
        occurred_at=None,
    )

    result = await service.create_activity(
        payload=payload,
        current_user_id=99,
    )

    assert result is activity
    db.add.assert_not_called()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_activity_vendor_contact_wrong_vendor():
    db, service = make_service()

    consultant = SimpleNamespace(id=10)
    vendor = SimpleNamespace(id=20)
    contact = SimpleNamespace(id=30, vendor_id=999)

    db.execute.side_effect = [
        scalar_result(consultant),
        scalar_result(vendor),
        scalar_result(contact),
    ]

    payload = SimpleNamespace(
        consultant_public_id=uuid4(),
        vendor_public_id=uuid4(),
        vendor_contact_public_id=uuid4(),
        client_public_id=None,
        activity_type="CALL",
        channel="PHONE",
        outcome="NO_ANSWER",
        subject="Call",
        notes="No answer",
        follow_up_required=False,
        occurred_at=None,
    )

    with pytest.raises(AppException) as exc_info:
        await service.create_activity(payload, 99)

    assert exc_info.value.status_code == 400
    assert "Vendor contact" in exc_info.value.message
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_activity_client_wrong_vendor():
    db, service = make_service()

    consultant = SimpleNamespace(id=10)
    vendor = SimpleNamespace(id=20)
    client = SimpleNamespace(id=40, vendor_id=999)

    db.execute.side_effect = [
        scalar_result(consultant),
        scalar_result(vendor),
        scalar_result(client),
    ]

    payload = SimpleNamespace(
        consultant_public_id=uuid4(),
        vendor_public_id=uuid4(),
        vendor_contact_public_id=None,
        client_public_id=uuid4(),
        activity_type="CALL",
        channel="PHONE",
        outcome="CONNECTED",
        subject="Call",
        notes="Client discussion",
        follow_up_required=False,
        occurred_at=None,
    )

    with pytest.raises(AppException) as exc_info:
        await service.create_activity(payload, 99)

    assert exc_info.value.status_code == 400
    assert "Client" in exc_info.value.message
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_activity_rolls_back_on_repository_error():
    db, service = make_service()

    consultant = SimpleNamespace(id=10)
    vendor = SimpleNamespace(id=20)

    db.execute.side_effect = [
        scalar_result(consultant),
        scalar_result(vendor),
    ]

    service.repository.create.side_effect = RuntimeError("database failure")

    payload = SimpleNamespace(
        consultant_public_id=uuid4(),
        vendor_public_id=uuid4(),
        vendor_contact_public_id=None,
        client_public_id=None,
        activity_type="EMAIL",
        channel="EMAIL",
        outcome="SENT",
        subject="Test",
        notes="Failure",
        follow_up_required=False,
        occurred_at=None,
    )

    with pytest.raises(RuntimeError, match="database failure"):
        await service.create_activity(payload, 99)

    db.rollback.assert_awaited_once()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_activity_success():
    db, service = make_service()

    activity = SimpleNamespace(public_id=uuid4())
    service.repository.get_by_public_id.return_value = activity

    result = await service.get_activity(activity.public_id)

    assert result is activity


@pytest.mark.asyncio
async def test_get_activity_not_found():
    db, service = make_service()
    service.repository.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc_info:
        await service.get_activity(uuid4())

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_list_consultant_activities_success():
    db, service = make_service()

    consultant = SimpleNamespace(id=55)
    activities = [SimpleNamespace(id=1), SimpleNamespace(id=2)]

    db.execute.return_value = scalar_result(consultant)
    service.repository.list_by_consultant.return_value = activities

    result = await service.list_consultant_activities(uuid4())

    assert result == activities
    service.repository.list_by_consultant.assert_awaited_once_with(55)


@pytest.mark.asyncio
async def test_create_activity_reload_failure():
    db, service = make_service()

    consultant = SimpleNamespace(id=10)
    vendor = SimpleNamespace(id=20)
    activity = SimpleNamespace(public_id=uuid4())

    db.execute.side_effect = [
        scalar_result(consultant),
        scalar_result(vendor),
    ]

    service.repository.create.return_value = activity
    service.repository.get_by_public_id.return_value = None

    payload = SimpleNamespace(
        consultant_public_id=uuid4(),
        vendor_public_id=uuid4(),
        vendor_contact_public_id=None,
        client_public_id=None,
        activity_type="EMAIL",
        channel="EMAIL",
        outcome="SENT",
        subject="Test",
        notes="Test",
        follow_up_required=False,
        occurred_at=None,
    )

    with pytest.raises(AppException) as exc_info:
        await service.create_activity(payload, 99)

    assert exc_info.value.status_code == 500
    db.rollback.assert_awaited_once()