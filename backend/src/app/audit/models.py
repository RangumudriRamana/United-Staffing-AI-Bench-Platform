from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import PrimaryKeyMixin, PublicIdMixin
from app.audit.enums import AuditActionType

class AuditRecord(Base, PrimaryKeyMixin, PublicIdMixin):
    """
    The permanent, append-only centralized system Audit Ledger.
    Captures exact state differentials alongside cross-context correlation trackers.
    """
    __tablename__ = "audit_records"

    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # --- Action & Context Parameters ---
    action_type: Mapped[AuditActionType] = mapped_column(SQLEnum(AuditActionType), index=True, nullable=False)
    source_context: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "SUBMISSION_SERVICE", "AUTH_MANAGER"
    correlation_id: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)

    # --- Polymorphic Target Reference Blocks ---
    entity_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # e.g., "CONSULTANT", "OFFER"
    entity_public_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    entity_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # --- Immutable State Snapshots ---
    before_snapshot_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_snapshot_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)