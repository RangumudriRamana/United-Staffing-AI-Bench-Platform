from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import PrimaryKeyMixin, PublicIdMixin, TimestampMixin
from app.communications.enums import CommunicationType, CommunicationDirection

class Communication(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """
    The central permanent Aggregate Root tracking interaction logs across the platform.
    Uses loose reference strings to bind across any operational domain module.
    """
    __tablename__ = "communications"

    sender_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # --- Classification Framework ---
    communication_type: Mapped[CommunicationType] = mapped_column(SQLEnum(CommunicationType), nullable=False)
    direction: Mapped[CommunicationDirection] = mapped_column(SQLEnum(CommunicationDirection), default=CommunicationDirection.INTERNAL, nullable=False)

    # --- Core Payloads ---
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # --- Polymorphic Context Linkages ---
    related_entity_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # e.g., "CONSULTANT", "REQUIREMENT"
    related_entity_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    # --- External Audit Trails ---
    external_reference: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)  # e.g., Message-ID headers
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True, nullable=False)