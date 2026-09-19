from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, Numeric, DateTime, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import PrimaryKeyMixin, PublicIdMixin, TimestampMixin
from app.submissions.enums import EmploymentType
from app.consultants.enums import DocumentType
from app.requirements.enums import RequirementStatus, WorkModel, RequirementPriority

class Requirement(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """
    The central commercial Aggregate Root tracking client positions, financial parameters,
    compliance restrictions, and the baseline tracking workflows.
    """
    __tablename__ = "requirements"

    # --- Structural Relational Anchors ---
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False)
    owner_recruiter_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # --- Job Description Metadata ---
    job_title: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    job_code: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, nullable=True)
    employment_type: Mapped[EmploymentType] = mapped_column(SQLEnum(EmploymentType), default=EmploymentType.C2C, nullable=False)
    work_model: Mapped[WorkModel] = mapped_column(SQLEnum(WorkModel), default=WorkModel.HYBRID, nullable=False)
    location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # --- Financial Constraints ---
    rate_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    rate_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    # --- Sourcing Qualifiers ---
    priority: Mapped[RequirementPriority] = mapped_column(SQLEnum(RequirementPriority), default=RequirementPriority.MEDIUM, nullable=False)
    status: Mapped[RequirementStatus] = mapped_column(SQLEnum(RequirementStatus), default=RequirementStatus.DRAFT, nullable=False)
    experience_min: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    experience_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    positions: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # --- Dates & Milestones ---
    received_date: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
    nullable=False,
    )

    target_start_date: Mapped[date | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # --- Structural ORM Connections ---
    technologies = relationship("RequirementTechnology", back_populates="requirement", cascade="all, delete-orphan")
    documents = relationship("RequirementDocument", back_populates="requirement", cascade="all, delete-orphan")
    history = relationship("RequirementHistory", back_populates="requirement", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="requirement")


class RequirementTechnology(Base, PrimaryKeyMixin, TimestampMixin):
    """Normalized structural bridge linking job requests back to canonical master skill IDs."""
    __tablename__ = "requirement_technologies"

    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False)
    technology_id: Mapped[int] = mapped_column(ForeignKey("technologies.id", ondelete="RESTRICT"), nullable=False)

    minimum_years: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    requirement = relationship("Requirement", back_populates="technologies")


class RequirementDocument(Base, PrimaryKeyMixin, TimestampMixin):
    """Enforces specific profile paperwork compliance guidelines ahead of external sourcing."""
    __tablename__ = "requirement_documents"

    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(SQLEnum(DocumentType), nullable=False)
    mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    requirement = relationship("Requirement", back_populates="documents")


class RequirementHistory(Base, PrimaryKeyMixin, TimestampMixin):
    """Immutable log ledger tracking tracking state progression across the sourcing lifecycle."""
    __tablename__ = "requirement_history"

    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False)
    changed_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[RequirementStatus] = mapped_column(SQLEnum(RequirementStatus), nullable=False)

    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    effective_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    requirement = relationship("Requirement", back_populates="history")
