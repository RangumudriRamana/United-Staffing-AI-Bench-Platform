from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, Numeric, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import PrimaryKeyMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin
from app.submissions.enums import (
    SubmissionStatus, EmploymentType, InterviewType, 
    InterviewStatus, OfferStatus, PlacementStatus
)

class Submission(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin):
    """
    The updated Submission Aggregate Root utilizing strict foreign relational keys
    while preserving immutable snapshot name states for deep audit consistency.
    """
    __tablename__ = "submissions"

    consultant_id: Mapped[int] = mapped_column(ForeignKey("consultants.id", ondelete="CASCADE"), nullable=False)
    submitted_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False)
    
    # 🎯 NEW FIRST-CLASS BRIDGE LINK: Reference the requirement aggregate root
    requirement_id: Mapped[int | None] = mapped_column(ForeignKey("requirements.id", ondelete="RESTRICT"), nullable=True)

    # --- Transitional Historical Snapshots ---
    client_name_snapshot: Mapped[str] = mapped_column(String(150), nullable=False)
    vendor_name_snapshot: Mapped[str] = mapped_column(String(150), nullable=False)
    job_title_snapshot: Mapped[str] = mapped_column(String(150), nullable=False)  # Added to protect query logs

    # --- Job Metadata & Financial Invariants ---
    job_title: Mapped[str] = mapped_column(String(150), nullable=False)
    job_location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    employment_type: Mapped[EmploymentType] = mapped_column(SQLEnum(EmploymentType), default=EmploymentType.C2C, nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    # --- Pipeline Management Flags ---
    submission_status: Mapped[SubmissionStatus] = mapped_column(SQLEnum(SubmissionStatus), default=SubmissionStatus.DRAFT, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expected_start_date: Mapped[date | None] = mapped_column(DateTime, nullable=True)

    # --- Structural ORM Connections ---
    client = relationship("Client", back_populates="submissions")
    requirement = relationship("Requirement", back_populates="submissions") # Added link back to requirement parent
    history = relationship("SubmissionHistory", back_populates="submission", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="submission", cascade="all, delete-orphan")
    feedback = relationship("ClientFeedback", back_populates="submission", cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="submission", cascade="all, delete-orphan")
    placements = relationship("Placement", back_populates="submission", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("consultant_id", "client_id", "job_title", name="uq_consultant_client_relational_job"),
    )

class SubmissionHistory(Base, PrimaryKeyMixin, TimestampMixin):
    """Immutable log ledger tracking state changes across the external submission pipeline."""
    __tablename__ = "submission_history"

    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    changed_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    status: Mapped[SubmissionStatus] = mapped_column(SQLEnum(SubmissionStatus), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    effective_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    submission = relationship("Submission", back_populates="history")


class Interview(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """Tracks chronological workflow loops for multi-round interviews."""
    __tablename__ = "interviews"

    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    interview_type: Mapped[InterviewType] = mapped_column(SQLEnum(InterviewType), nullable=False)
    status: Mapped[InterviewStatus] = mapped_column(SQLEnum(InterviewStatus), default=InterviewStatus.SCHEDULED, nullable=False)
    
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    interviewer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    feedback: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    submission = relationship("Submission", back_populates="interviews")


class ClientFeedback(Base, PrimaryKeyMixin, TimestampMixin):
    """Captures formal rating indexes and coaching notes directly from external reviewers."""
    __tablename__ = "client_feedbacks"

    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., Hiring Manager Name
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # e.g., Scale 1-5 or 1-10
    feedback: Mapped[str] = mapped_column(String(1000), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    submission = relationship("Submission", back_populates="feedback")


class Offer(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """Tracks formalized client offer letters ahead of placement conversions."""
    __tablename__ = "offers"

    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    offered_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    start_date: Mapped[date] = mapped_column(DateTime, nullable=False)
    expiration_date: Mapped[date | None] = mapped_column(DateTime, nullable=True)
    offer_status: Mapped[OfferStatus] = mapped_column(SQLEnum(OfferStatus), default=OfferStatus.PENDING, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    submission = relationship("Submission", back_populates="offers")


class Placement(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """The final closing link mapping placed consultants to active revenue projects."""
    __tablename__ = "placements"

    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    started_on: Mapped[date] = mapped_column(DateTime, nullable=False)
    ended_on: Mapped[date | None] = mapped_column(DateTime, nullable=True)
    
    billing_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)  # What we bill the client
    pay_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)      # What we pay the candidate
    placement_status: Mapped[PlacementStatus] = mapped_column(SQLEnum(PlacementStatus), default=PlacementStatus.ACTIVE, nullable=False)

    submission = relationship("Submission", back_populates="placements")