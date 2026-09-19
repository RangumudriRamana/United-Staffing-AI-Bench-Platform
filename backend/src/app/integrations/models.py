from datetime import datetime
from sqlalchemy import String, Integer, Enum as SQLEnum, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import PrimaryKeyMixin, PublicIdMixin, TimestampMixin
from app.integrations.enums import IntegrationType, IntegrationStatus, SyncStatus

class IntegrationConnection(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """
    The central Aggregate Root representing an external third-party API link context.
    Stores structural routing metadata blocks while hiding secrets behind credential references.
    """
    __tablename__ = "integration_connections"

    provider_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)  # e.g., "GOOGLE_WORKSPACE", "BULLHORN"
    integration_type: Mapped[IntegrationType] = mapped_column(SQLEnum(IntegrationType), index=True, nullable=False)
    status: Mapped[IntegrationStatus] = mapped_column(SQLEnum(IntegrationStatus), default=IntegrationStatus.CONNECTED, nullable=False)
    
    # Secure storage configurations mapping parameters dynamically
    configuration_json: Mapped[dict | None] = mapped_column(JSON, nullable=True) # e.g., {"api_endpoint": "https://..."}
    credentials_reference: Mapped[str | None] = mapped_column(String(255), nullable=True) # Vault/Secret Manager key target reference
    
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # --- Structural ORM Connections ---
    sync_states = relationship("SyncState", back_populates="connection", cascade="all, delete-orphan")


class SyncState(Base, PrimaryKeyMixin, TimestampMixin):
    """Immutable data tracking row logging background synchronization states and transaction records."""
    __tablename__ = "integration_sync_states"

    integration_connection_id: Mapped[int] = mapped_column(ForeignKey("integration_connections.id", ondelete="CASCADE"), nullable=False)
    
    status: Mapped[SyncStatus] = mapped_column(SQLEnum(SyncStatus), default=SyncStatus.SYNCHRONIZED, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    external_reference: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True) # Target system unique identifier
    
    last_success: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_failure: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_log: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # --- Structural ORM Connections ---
    connection = relationship("IntegrationConnection", back_populates="sync_states")