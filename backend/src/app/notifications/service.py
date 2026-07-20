from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.notifications.models import Notification
from app.notifications.enums import NotificationStatus
from app.notifications.schemas import NotificationCreatePayload

class NotificationService:
    """
    Decoupled business domain engine orchestration layer managing delivery actions,
    status tracking modifications, and list fetches.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_system_notification(self, payload: NotificationCreatePayload) -> Notification:
        """Instantiates record definitions and registers delivery pipeline triggers."""
        new_alert = Notification(
            recipient_id=payload.recipient_id,
            notification_type=payload.notification_type,
            priority=payload.priority,
            delivery_channel=payload.delivery_channel,
            title=payload.title,
            body=payload.body,
            status=NotificationStatus.UNREAD
        )
        self.db.add(new_alert)
        await self.db.commit()
        
        # NOTE: Connect future external background handlers (SendGrid, Twilio, Slack Webhooks)
        # down here to trigger depending on selected delivery_channel type parameters.
        return new_alert

    async def mark_notification_as_read(self, public_id: UUID, recipient_user_id: int) -> Notification:
        """Locates targeted row records and seals the read timestamp parameters safely."""
        stmt = select(Notification).where(Notification.public_id == public_id)
        res = await self.db.execute(stmt)
        alert = res.scalars().first()

        if not alert:
            raise AppException(status_code=404, message="Target notification record not found.")
        if alert.recipient_id != recipient_user_id:
            raise AppException(status_code=403, message="Unauthorized interaction context boundary.")

        alert.status = NotificationStatus.READ
        alert.read_at = datetime.now(timezone.utc)
        await self.db.commit()
        return alert

    async def fetch_user_unread_alerts(self, recipient_user_id: int) -> list[Notification]:
        """Queries database partitions to collect active message logs for home screens."""
        stmt = (
            select(Notification)
            .where(
                Notification.recipient_id == recipient_user_id,
                Notification.status == NotificationStatus.UNREAD
            )
            .order_by(Notification.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())