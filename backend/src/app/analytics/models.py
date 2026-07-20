from datetime import datetime
from sqlalchemy import String, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import PrimaryKeyMixin, PublicIdMixin

class BusinessEvent(Base, PrimaryKeyMixin, PublicIdMixin):
    """
    The centralized infrastructure event log ledger. Captures decoupled structural
    snapshots of business process evolutions without locking active transactional entities.
    """
    __tablename__ = "business_events"

    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False) # e.g., "SUBMISSION", "REQUIREMENT"
    aggregate_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    
    actor_id: Mapped[int | None] = mapped_column(Integer, nullable=True) # User execution signature tracking
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    
    # Flexible container block for arbitrary snapshot logs
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)