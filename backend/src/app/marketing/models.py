from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import PrimaryKeyMixin, PublicIdMixin, TimestampMixin
from app.marketing.enums import MarketingActivityType, MarketingChannel, MarketingOutcome


class MarketingActivity(
    Base,
    PrimaryKeyMixin,
    PublicIdMixin,
    TimestampMixin,
):
    """
    Permanent operational record of a consultant marketing activity.

    A MarketingActivity represents what actually happened during
    consultant marketing. Follow-up work is represented separately
    through the existing Task domain.
    """

    __tablename__ = "marketing_activities"

    # ==========================================================
    # Core Relationships
    # ==========================================================

    consultant_id: Mapped[int] = mapped_column(
        ForeignKey("consultants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    vendor_id: Mapped[int] = mapped_column(
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    vendor_contact_id: Mapped[int | None] = mapped_column(
        ForeignKey("vendor_contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    performed_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

        # ==========================================================
    # ORM Relationships
    # ==========================================================

    consultant = relationship(
        "Consultant",
        foreign_keys=[consultant_id],
    )

    vendor = relationship(
        "Vendor",
        foreign_keys=[vendor_id],
    )

    vendor_contact = relationship(
        "VendorContact",
        foreign_keys=[vendor_contact_id],
    )

    client = relationship(
        "Client",
        foreign_keys=[client_id],
    )

    performer = relationship(
        "User",
        foreign_keys=[performed_by],
    )

    # ==========================================================
    # Public-ID Convenience Properties
    # ==========================================================

    @property
    def consultant_public_id(self):
        return self.consultant.public_id if self.consultant else None

    @property
    def vendor_public_id(self):
        return self.vendor.public_id if self.vendor else None

    @property
    def vendor_contact_public_id(self):
        return (
            self.vendor_contact.public_id
            if self.vendor_contact
            else None
        )

    @property
    def client_public_id(self):
        return self.client.public_id if self.client else None

    # ==========================================================
    # Activity Classification
    # ==========================================================

    activity_type: Mapped[MarketingActivityType] = mapped_column(
        SQLEnum(MarketingActivityType),
        nullable=False,
        index=True,
    )

    channel: Mapped[MarketingChannel] = mapped_column(
        SQLEnum(MarketingChannel),
        nullable=False,
    )

    outcome: Mapped[MarketingOutcome] = mapped_column(
        SQLEnum(MarketingOutcome),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # Operational Details
    # ==========================================================

    subject: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    follow_up_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )