from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.notifications.router import (
    acknowledge_notification_alert,
    get_notification_service,
    list_active_unread_notifications,
)


@pytest.mark.asyncio
async def test_get_notification_service():
    db = MagicMock()

    result = await get_notification_service(db)

    assert result.db is db


@pytest.mark.asyncio
async def test_list_active_unread_notifications():
    service = MagicMock()
    service.fetch_user_unread_alerts = AsyncMock(
        return_value=["notification-1", "notification-2"]
    )

    current_user = MagicMock()
    current_user.id = 123

    result = await list_active_unread_notifications(
        current_user=current_user,
        service=service,
        _role="ADMIN",
    )

    assert result == ["notification-1", "notification-2"]

    service.fetch_user_unread_alerts.assert_awaited_once_with(
        recipient_user_id=123,
    )


@pytest.mark.asyncio
async def test_acknowledge_notification_alert():
    service = MagicMock()
    service.mark_notification_as_read = AsyncMock(
        return_value="notification"
    )

    current_user = MagicMock()
    current_user.id = 456

    public_id = uuid4()

    result = await acknowledge_notification_alert(
        public_id=public_id,
        current_user=current_user,
        service=service,
        _role="RECRUITER",
    )

    assert result == "notification"

    service.mark_notification_as_read.assert_awaited_once_with(
        public_id=public_id,
        recipient_user_id=456,
    )