from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
)


class AIMatchHistory(Base, PrimaryKeyMixin, TimestampMixin):
    """
    Immutable record of an AI consultant-to-requirement match.

    Each matching execution creates one history record per
    consultant evaluated against the requirement.
    """

    __tablename__ = "ai_match_history"

    consultant_id: Mapped[int] = mapped_column(
        ForeignKey("consultants.id", ondelete="CASCADE"),
        nullable=False,
    )

    requirement_id: Mapped[int] = mapped_column(
        ForeignKey("requirements.id", ondelete="CASCADE"),
        nullable=False,
    )

    match_score: Mapped[float] = mapped_column(
        nullable=False,
    )

    recommendation: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    matched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    consultant = relationship("Consultant")
    requirement = relationship("Requirement")

    __table_args__ = (
        Index(
            "ix_ai_match_history_consultant",
            "consultant_id",
        ),
        Index(
            "ix_ai_match_history_requirement",
            "requirement_id",
        ),
        Index(
            "ix_ai_match_history_matched_at",
            "matched_at",
        ),
    )