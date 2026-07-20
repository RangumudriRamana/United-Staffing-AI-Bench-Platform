from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, Boolean, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import PrimaryKeyMixin, PublicIdMixin, TimestampMixin
from app.automation.enums import AutomationTriggerType, ExecutionStatus

class WorkflowRule(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """
    The Aggregate Root governing automated tracking rules.
    Stores structured condition and action logic trees inside flexible JSON containers.
    """
    __tablename__ = "workflow_rules"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    trigger_type: Mapped[AutomationTriggerType] = mapped_column(SQLEnum(AutomationTriggerType), index=True, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Structured configurations mapping parameters dynamically
    condition_json: Mapped[dict | None] = mapped_column(JSON, nullable=True) # e.g., {"aging_days": 5}
    action_json: Mapped[dict] = mapped_column(JSON, nullable=False)          # e.g., [{"action_type": "CREATE_TASK", "payload": {...}}]

    # --- Structural ORM Connections ---
    executions = relationship("WorkflowExecution", back_populates="rule", cascade="all, delete-orphan")


class WorkflowExecution(Base, PrimaryKeyMixin, TimestampMixin):
    """Immutable audit trail logging background execution metrics and diagnostic exceptions."""
    __tablename__ = "workflow_executions"

    workflow_rule_id: Mapped[int] = mapped_column(ForeignKey("workflow_rules.id", ondelete="CASCADE"), nullable=False)
    
    trigger_event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[ExecutionStatus] = mapped_column(SQLEnum(ExecutionStatus), nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # --- Structural ORM Connections ---
    rule = relationship("WorkflowRule", back_populates="executions")