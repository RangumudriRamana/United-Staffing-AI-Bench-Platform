from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from app.notifications.enums import NotificationType, DeliveryChannel, NotificationPriority, NotificationStatus

class NotificationCreatePayload(BaseModel):
    """Payload parameter model structure used by internal service event publishers."""
    recipient_id: int
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    delivery_channel: DeliveryChannel = DeliveryChannel.IN_APP
    title: str
    body: str

class NotificationResponse(BaseModel):
    """Outbound serialization DTO serving alerts straight to dashboard modules."""
    public_id: UUID
    recipient_id: int
    notification_type: NotificationType
    priority: NotificationPriority
    status: NotificationStatus
    delivery_channel: DeliveryChannel
    title: str
    body: str
    created_at: datetime
    read_at: datetime | None

    class Config:
        from_attributes = True