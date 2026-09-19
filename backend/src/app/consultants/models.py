from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, Boolean, Date, Numeric, ForeignKey, Enum as SQLEnum, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import PrimaryKeyMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, ReferenceMixin
from app.consultants.enums import AvailabilityStatus, VisaStatus, MarketingStatus, RateType, ProficiencyLevel


class TechnologyCategory(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin, ReferenceMixin):
    """
    Hierarchical category system allowing nested skill classifications 
    (e.g., Software -> Backend -> Python).
    """
    __tablename__ = "technology_categories"

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("technology_categories.id", ondelete="CASCADE"), nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Self-referential relationships for hierarchical nesting
    parent = relationship("TechnologyCategory", remote_side="TechnologyCategory.id", back_populates="children")
    children = relationship("TechnologyCategory", back_populates="parent", cascade="all, delete-orphan")
    technologies = relationship("Technology", back_populates="category")


class Technology(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin, ReferenceMixin):
    """
    Master Catalog table representing canonical software skills, frameworks, and tools.
    """
    __tablename__ = "technologies"

    category_id: Mapped[int] = mapped_column(
        ForeignKey("technology_categories.id", ondelete="RESTRICT"), nullable=False
    )
    
    # Structural ORM Relationships
    category = relationship("TechnologyCategory", back_populates="technologies")
    aliases = relationship("TechnologyAlias", back_populates="technology", cascade="all, delete-orphan")


class TechnologyAlias(Base, PrimaryKeyMixin, TimestampMixin):
    """
    Maps synonymous terms or typos (e.g., 'ReactJS', 'React.js') 
    directly to a single canonical Technology record.
    """
    __tablename__ = "technology_aliases"

    technology_id: Mapped[int] = mapped_column(
        ForeignKey("technologies.id", ondelete="CASCADE"), nullable=False
    )
    alias: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    # Structural ORM Relationships
    technology = relationship("Technology", back_populates="aliases")


class Consultant(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin):
    """
    The Core Aggregate Root representing a professional consultant on the bench.
    """
    __tablename__ = "consultants"

    # --- Identity Cluster ---
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # --- Professional Matrix ---
    current_title: Mapped[str | None] = mapped_column(String(150), nullable=True)
    total_experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    preferred_location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    relocation_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    remote_preference: Mapped[str] = mapped_column(String(50), default="Hybrid", nullable=False)

    # --- Work Authorization ---
    visa_status: Mapped[VisaStatus] = mapped_column(SQLEnum(VisaStatus), nullable=False)
    visa_expiration: Mapped[date | None] = mapped_column(Date, nullable=True)
    work_authorized: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # --- Bench Marketing & Availability Attributes ---
    marketing_status: Mapped[MarketingStatus] = mapped_column(
        SQLEnum(MarketingStatus), default=MarketingStatus.NEW, nullable=False
    )
    availability_status: Mapped[AvailabilityStatus] = mapped_column(
        SQLEnum(AvailabilityStatus), default=AvailabilityStatus.AVAILABLE_NOW, nullable=False
    )
    availability_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    rate_type: Mapped[RateType] = mapped_column(SQLEnum(RateType), default=RateType.HOURLY, nullable=False)
    expected_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    # --- Ownership Boundaries ---
    recruiter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # --- Structural ORM Relationships (Always keep at the bottom) ---
    recruiter = relationship("User", foreign_keys=[recruiter_id])
    marketing_history = relationship("ConsultantMarketingHistory", back_populates="consultant", cascade="all, delete-orphan")
    technologies = relationship("ConsultantTechnology", back_populates="consultant", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="consultant", cascade="all, delete-orphan")

class ConsultantTechnology(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin):
    """
    Tracks a consultant's hands-on experience and proficiency metrics for a technology.
    """
    __tablename__ = "consultant_technologies"

    consultant_id: Mapped[int] = mapped_column(ForeignKey("consultants.id", ondelete="CASCADE"), nullable=False)
    technology_id: Mapped[int] = mapped_column(ForeignKey("technologies.id", ondelete="RESTRICT"), nullable=False)

    years_of_experience: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    proficiency_level: Mapped[ProficiencyLevel] = mapped_column(
        SQLEnum(ProficiencyLevel), default=ProficiencyLevel.INTERMEDIATE, nullable=False
    )
    last_used_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    currently_using: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    consultant = relationship("Consultant", back_populates="technologies")
    technology = relationship("Technology")

    __table_args__ = (
        UniqueConstraint("consultant_id", "technology_id", name="uq_consultant_technology"),
        Index("ix_consultant_tech_lookup", "consultant_id", "technology_id"),
        Index("ix_consultant_tech_search_metrics", "technology_id", "is_primary", "currently_using", "proficiency_level"),
    )

from app.consultants.enums import DocumentType

class Document(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin):
    """
    Generic Document entity capturing file metadata, immutable version tracking states, 
    and cloud storage keys linked back to a core consultant aggregate root.
    """
    __tablename__ = "documents"

    # --- Parent Boundaries ---
    consultant_id: Mapped[int] = mapped_column(ForeignKey("consultants.id", ondelete="CASCADE"), nullable=False)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # --- Document Characteristics ---
    document_type: Mapped[DocumentType] = mapped_column(SQLEnum(DocumentType), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)  # Unique path/URL in S3 or local disk storage
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)  # SHA-256 file verification checksum

    # --- State & Version Control ---
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # --- Structural ORM Relationships ---
    consultant = relationship("Consultant", back_populates="documents")


class ConsultantMarketingHistory(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """
    Event Log ledger capturing state transition histories across marketing cycles.
    Enables rich chronological trace metrics for performance operational reporting.
    """
    __tablename__ = "consultant_marketing_history"

    consultant_id: Mapped[int] = mapped_column(ForeignKey("consultants.id", ondelete="CASCADE"), nullable=False)
    changed_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    status: Mapped[MarketingStatus] = mapped_column(SQLEnum(MarketingStatus), nullable=False)
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

    # Structural ORM Connections
    consultant = relationship("Consultant", back_populates="marketing_history")