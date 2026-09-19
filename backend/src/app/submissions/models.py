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
    Core Submission Aggregate Root.
    Represents one consultant submission to a specific client/job.
    """

    __tablename__ = "submissions"

    consultant_id: Mapped[int] = mapped_column(ForeignKey("consultants.id", ondelete="CASCADE"),nullable=False,)

    submitted_by: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False,)

    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id", ondelete="RESTRICT"),nullable=False,)

    vendor_contact_id: Mapped[int | None] = mapped_column(ForeignKey("vendor_contacts.id", ondelete="SET NULL"),nullable=True,)

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="RESTRICT"),nullable=False,)

    requirement_id: Mapped[int | None] = mapped_column(ForeignKey("requirements.id", ondelete="RESTRICT"),nullable=True,)

    client_name_snapshot: Mapped[str] = mapped_column(String(150),nullable=False,)

    vendor_name_snapshot: Mapped[str] = mapped_column(String(150),nullable=False,)

    job_title_snapshot: Mapped[str] = mapped_column(String(150),nullable=False,)

    job_id: Mapped[str | None] = mapped_column(String(100),nullable=True,index=True,)

    job_title: Mapped[str] = mapped_column(String(150),nullable=False,)

    job_location: Mapped[str | None] = mapped_column(String(150),nullable=True,)

    employment_type: Mapped[EmploymentType] = mapped_column(SQLEnum(EmploymentType),default=EmploymentType.C2C,nullable=False,)

    rate: Mapped[Decimal] = mapped_column(Numeric(10, 2),nullable=False,)

    currency: Mapped[str] = mapped_column(String(3),default="USD",nullable=False,)

    submission_status: Mapped[SubmissionStatus] = mapped_column(SQLEnum(SubmissionStatus),default=SubmissionStatus.DRAFT,nullable=False,)

    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow,nullable=False,)

    expected_start_date: Mapped[date | None] = mapped_column(nullable=True,)

    submission_notes: Mapped[str | None] = mapped_column(String(2000),nullable=True,)

    consultant = relationship("Consultant")
    vendor = relationship("Vendor")
    vendor_contact = relationship("VendorContact")
    client = relationship("Client", back_populates="submissions")
    submitted_by_user = relationship("User", foreign_keys=[submitted_by])

    requirement = relationship("Requirement",back_populates="submissions",)

    history = relationship("SubmissionHistory",back_populates="submission",cascade="all, delete-orphan",)

    interviews = relationship("Interview",back_populates="submission",cascade="all, delete-orphan",)

    feedback = relationship("ClientFeedback",back_populates="submission",cascade="all, delete-orphan",)

    offers = relationship("Offer",back_populates="submission",cascade="all, delete-orphan",)

    placements = relationship("Placement",back_populates="submission",cascade="all, delete-orphan",)

    __table_args__ = (UniqueConstraint("consultant_id","vendor_id","client_id","job_id",name="uq_submission_unique",),
        Index(
            "ix_submission_status",
            "submission_status",
        ),
        Index(
            "ix_submission_submitted_at",
            "submitted_at",
        ),
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

    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"),nullable=False,)

    offered_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2),nullable=False,)

    currency: Mapped[str] = mapped_column(String(3),default="USD",nullable=False,)

    start_date: Mapped[date] = mapped_column(nullable=False,)

    expiration_date: Mapped[date | None] = mapped_column(nullable=True,)

    offer_status: Mapped[OfferStatus] = mapped_column(SQLEnum(OfferStatus),default=OfferStatus.PENDING,nullable=False,)

    notes: Mapped[str | None] = mapped_column(String(500),nullable=True,)

    submission = relationship("Submission",back_populates="offers",)


class Placement(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """The final closing link mapping placed consultants to active revenue projects."""
    __tablename__ = "placements"

    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"),nullable=False,)

    started_on: Mapped[date] = mapped_column(nullable=False,)

    ended_on: Mapped[date | None] = mapped_column(nullable=True,)

    billing_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2),nullable=False,)

    pay_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2),nullable=False,)

    placement_status: Mapped[PlacementStatus] = mapped_column(SQLEnum(PlacementStatus),default=PlacementStatus.ACTIVE,nullable=False,)

    submission = relationship("Submission",back_populates="placements",)