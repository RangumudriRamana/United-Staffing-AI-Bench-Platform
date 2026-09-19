from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import PrimaryKeyMixin, PublicIdMixin, TimestampMixin
from app.vendors.enums import VendorType, VendorTier, VendorStatus

class Vendor(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """
    The Aggregate Root entity representing an external vendor agency or staff company partner.
    Tracks structural contract tier profiles and aggregate commercial performance shortcuts.
    """
    __tablename__ = "vendors"

    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    vendor_type: Mapped[VendorType] = mapped_column(SQLEnum(VendorType), default=VendorType.PRIME_VENDOR, nullable=False)
    tier: Mapped[VendorTier] = mapped_column(SQLEnum(VendorTier), default=VendorTier.TIER_2, nullable=False)
    status: Mapped[VendorStatus] = mapped_column(SQLEnum(VendorStatus), default=VendorStatus.ACTIVE, nullable=False)
    
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preferred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"),nullable=True,)

    # --- Structural ORM Connections ---
    contacts = relationship("VendorContact", back_populates="vendor", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="vendor", cascade="all, delete-orphan")


class VendorContact(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """
    Represents individual accounts, account managers, or recruiters employed by a vendor partner.
    Acts as the direct target touchpoint for submission engagement timelines.
    """
    __tablename__ = "vendor_contacts"

    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g., Senior Account Manager
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    linkedin: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    timezone: Mapped[str] = mapped_column(String(50), default="EST", nullable=False)
    preferred_contact: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_contacted: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # --- Structural ORM Connections ---
    vendor = relationship("Vendor", back_populates="contacts")

from app.vendors.enums import ClientStatus

class Client(Base, PrimaryKeyMixin, PublicIdMixin, TimestampMixin):
    """
    Represents the end customer receiving professional staffing services.
    Linked firmly back to the corresponding Vendor broker context.
    """
    __tablename__ = "clients"

    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # --- Structural Demographics Matrix ---
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="EST", nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # --- Governance States ---
    status: Mapped[ClientStatus] = mapped_column(SQLEnum(ClientStatus), default=ClientStatus.ACTIVE, nullable=False)
    preferred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # --- Structural ORM Connections ---
    vendor = relationship("Vendor", back_populates="clients")
    submissions = relationship("Submission", back_populates="client")

    @property
    def vendor_public_id(self):
        return self.vendor.public_id if self.vendor else None

    __table_args__ = (
        # Localized Uniqueness Guard: Enforce unique names per vendor sandbox
        UniqueConstraint("vendor_id", "name", name="uq_vendor_client_name"),
    )