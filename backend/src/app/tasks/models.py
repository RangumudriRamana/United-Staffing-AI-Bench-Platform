from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import PrimaryKeyMixin, PublicIdMixin, TimestampMixin

from app.tasks.enums import TaskType, TaskStatus, TaskPriority

class Task(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """
    The main structural Aggregate Root representing an actionable operational task assignment.
    Utilizes generic reference parameters to bind seamlessly across decoupled domain entities.
    """
    __tablename__ = "tasks"

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # --- Classification & Control Vectors ---
    task_type: Mapped[TaskType] = mapped_column(SQLEnum(TaskType), nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(SQLEnum(TaskPriority), default=TaskPriority.NORMAL, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.OPEN, nullable=False)

    # --- Core Payloads ---
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # --- Generic Bounded Reference Links ---
    related_entity_type: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True) # e.g., "CONSULTANT"
    related_entity_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)

    # --- Deadlines & Tracking Stamps ---
    due_at: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)