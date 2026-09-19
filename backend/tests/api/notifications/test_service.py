from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

from app.core.exceptions import AppException
from app.notifications.enums import NotificationStatus
from app.notifications.service import NotificationService


def make_service():
    db = MagicMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()

    service = NotificationService(db)

    return service, db


def make_payload():
    return SimpleNamespace(
        recipient_id=99,
        notification_type="SYSTEM",
        priority="NORMAL",
        delivery_channel="IN_APP",
        title="Test Notification",
        body="Test notification body",
    )


def make_notification(
    recipient_id=99,
    status=NotificationStatus.UNREAD,
):
    return SimpleNamespace(
        public_id=UUID("11111111-1111-1111-1111-111111111111"),
        recipient_id=recipient_id,
        status=status,
        read_at=None,
    )


def make_query_result(value):
    result = MagicMock()
    result.scalars.return_value.first.return_value = value
    return result


# ---------------------------------------------------------------------------
# create_system_notification
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_system_notification_success():
    service, db = make_service()

    payload = make_payload()
    notification = make_notification()

    with patch(
        "app.notifications.service.Notification",
        return_value=notification,
    ) as notification_cls:
        result = await service.create_system_notification(payload)

    assert result is notification

    notification_cls.assert_called_once_with(
        recipient_id=payload.recipient_id,
        notification_type=payload.notification_type,
        priority=payload.priority,
        delivery_channel=payload.delivery_channel,
        title=payload.title,
        body=payload.body,
        status=NotificationStatus.UNREAD,
    )

    db.add.assert_called_once_with(notification)
    db.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# mark_notification_as_read
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mark_notification_as_read_success():
    service, db = make_service()

    notification = make_notification()

    db.execute.return_value = make_query_result(notification)

    result = await service.mark_notification_as_read(
        public_id=notification.public_id,
        recipient_user_id=99,
    )

    assert result is notification
    assert notification.status == NotificationStatus.READ
    assert notification.read_at is not None
    assert notification.read_at.tzinfo is not None

    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_mark_notification_as_read_not_found():
    service, db = make_service()

    db.execute.return_value = make_query_result(None)

    public_id = UUID("11111111-1111-1111-1111-111111111111")

    with pytest.raises(AppException) as exc:
        await service.mark_notification_as_read(
            public_id=public_id,
            recipient_user_id=99,
        )

    assert exc.value.status_code == 404
    assert exc.value.message == "Target notification record not found."

    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_mark_notification_as_read_forbidden_for_wrong_recipient():
    service, db = make_service()

    notification = make_notification(recipient_id=100)

    db.execute.return_value = make_query_result(notification)

    with pytest.raises(AppException) as exc:
        await service.mark_notification_as_read(
            public_id=notification.public_id,
            recipient_user_id=99,
        )

    assert exc.value.status_code == 403
    assert exc.value.message == "Unauthorized interaction context boundary."

    assert notification.status == NotificationStatus.UNREAD
    assert notification.read_at is None
    db.commit.assert_not_awaited()


# ---------------------------------------------------------------------------
# fetch_user_unread_alerts
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_user_unread_alerts_returns_notifications():
    service, db = make_service()

    notification_1 = make_notification()
    notification_2 = make_notification()

    result = MagicMock()
    result.scalars.return_value.all.return_value = [
        notification_1,
        notification_2,
    ]

    db.execute.return_value = result

    alerts = await service.fetch_user_unread_alerts(
        recipient_user_id=99,
    )

    assert alerts == [notification_1, notification_2]
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_user_unread_alerts_returns_empty_list():
    service, db = make_service()

    result = MagicMock()
    result.scalars.return_value.all.return_value = []

    db.execute.return_value = result

    alerts = await service.fetch_user_unread_alerts(
        recipient_user_id=99,
    )

    assert alerts == []
    db.execute.assert_awaited_once()