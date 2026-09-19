from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.exceptions import AppException
from app.notifications.enums import NotificationStatus
from app.notifications.service import NotificationService


def make_service():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.execute = AsyncMock()
    return db, NotificationService(db)


def scalar_result(value):
    result = MagicMock()
    result.scalars.return_value.first.return_value = value
    return result


@pytest.mark.asyncio
async def test_create_system_notification():
    db, service = make_service()

    payload = SimpleNamespace(
        recipient_id=10,
        notification_type="SYSTEM",
        priority="NORMAL",
        delivery_channel="IN_APP",
        title="New requirement",
        body="A new requirement was assigned.",
    )

    result = await service.create_system_notification(payload)

    db.add.assert_called_once()
    db.commit.assert_awaited_once()

    assert result.recipient_id == 10
    assert result.notification_type == "SYSTEM"
    assert result.priority == "NORMAL"
    assert result.delivery_channel == "IN_APP"
    assert result.title == "New requirement"
    assert result.body == "A new requirement was assigned."
    assert result.status == NotificationStatus.UNREAD


@pytest.mark.asyncio
async def test_mark_notification_as_read_success():
    db, service = make_service()

    public_id = uuid4()
    notification = SimpleNamespace(
        public_id=public_id,
        recipient_id=10,
        status=NotificationStatus.UNREAD,
        read_at=None,
    )

    db.execute.return_value = scalar_result(notification)

    result = await service.mark_notification_as_read(
        public_id=public_id,
        recipient_user_id=10,
    )

    assert result is notification
    assert notification.status == NotificationStatus.READ
    assert notification.read_at is not None
    assert notification.read_at.tzinfo is not None
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_mark_notification_as_read_not_found():
    db, service = make_service()

    db.execute.return_value = scalar_result(None)

    with pytest.raises(AppException) as exc_info:
        await service.mark_notification_as_read(uuid4(), 10)

    assert exc_info.value.status_code == 404
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_mark_notification_as_read_wrong_recipient():
    db, service = make_service()

    notification = SimpleNamespace(
        public_id=uuid4(),
        recipient_id=99,
        status=NotificationStatus.UNREAD,
        read_at=None,
    )

    db.execute.return_value = scalar_result(notification)

    with pytest.raises(AppException) as exc_info:
        await service.mark_notification_as_read(
            public_id=notification.public_id,
            recipient_user_id=10,
        )

    assert exc_info.value.status_code == 403
    assert notification.status == NotificationStatus.UNREAD
    assert notification.read_at is None
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_fetch_user_unread_alerts():
    db, service = make_service()

    alerts = [
        SimpleNamespace(id=1, status=NotificationStatus.UNREAD),
        SimpleNamespace(id=2, status=NotificationStatus.UNREAD),
    ]

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.all.return_value = alerts
    db.execute.return_value = result_proxy

    result = await service.fetch_user_unread_alerts(10)

    assert result == alerts
    assert len(result) == 2
    assert all(
        alert.status == NotificationStatus.UNREAD
        for alert in result
    )


@pytest.mark.asyncio
async def test_fetch_user_unread_alerts_empty():
    db, service = make_service()

    result_proxy = MagicMock()
    result_proxy.scalars.return_value.all.return_value = []
    db.execute.return_value = result_proxy

    result = await service.fetch_user_unread_alerts(999)

    assert result == []