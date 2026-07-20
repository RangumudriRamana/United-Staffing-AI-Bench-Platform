from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, Boolean, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import PrimaryKeyMixin, PublicIdMixin, TimestampMixin
from app.reporting.enums import ReportCategory, ExportFormat, ReportExecutionStatus

class ReportDefinition(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """
    The Aggregate Root structure representing a reusable reporting profile template.
    Defines parameter rules and execution metrics criteria records.
    """
    __tablename__ = "report_definitions"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    report_type: Mapped[ReportCategory] = mapped_column(SQLEnum(ReportCategory), index=True, nullable=False)
    output_format: Mapped[ExportFormat] = mapped_column(SQLEnum(ExportFormat), default=ExportFormat.CSV, nullable=False)
    
    # Flexible structured configurations mapping target parameters
    parameters_json: Mapped[dict | None] = mapped_column(JSON, nullable=True) # e.g., {"date_from": "2026-01-01"}
    schedule: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Cron formatting properties
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # --- Structural ORM Connections ---
    executions = relationship("ReportExecution", back_populates="definition", cascade="all, delete-orphan")


class ReportExecution(Base, PrimaryKeyMixin, TimestampMixin):
    """Immutable point-in-time logging ledger tracking historical report file exports."""
    __tablename__ = "report_executions"

    report_definition_id: Mapped[int] = mapped_column(ForeignKey("report_definitions.id", ondelete="CASCADE"), nullable=False)
    generated_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    status: Mapped[ReportExecutionStatus] = mapped_column(SQLEnum(ReportExecutionStatus), default=ReportExecutionStatus.PENDING, nullable=False)
    file_location: Mapped[str | None] = mapped_column(String(500), nullable=True) # Storage path reference target
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # --- Structural ORM Connections ---
    definition = relationship("ReportDefinition", back_populates="executions")