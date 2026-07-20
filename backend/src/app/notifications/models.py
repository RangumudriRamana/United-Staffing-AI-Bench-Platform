from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import PrimaryKeyMixin, PublicIdMixin, TimestampMixin
from app.notifications.enums import NotificationType, DeliveryChannel, NotificationPriority, NotificationStatus

class Notification(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """
    The main aggregate entry representing a unified alert message payload.
    Dispatched asynchronously to individual users across targeted communication profiles.
    """
    __tablename__ = "notifications"

    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # --- Context Type Mappings ---
    notification_type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType), nullable=False)
    priority: Mapped[NotificationPriority] = mapped_column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(SQLEnum(NotificationStatus), default=NotificationStatus.UNREAD, nullable=False)
    delivery_channel: Mapped[DeliveryChannel] = mapped_column(SQLEnum(DeliveryChannel), default=DeliveryChannel.IN_APP, nullable=False)

    # --- Content Payload Data ---
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(String(1000), nullable=False)

    # --- Timeline Management Milestones ---
    scheduled_for: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)