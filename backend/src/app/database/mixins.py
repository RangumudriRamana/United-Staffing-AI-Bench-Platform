from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.identifiers import generate_public_id

def utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


class PrimaryKeyMixin:
    """Reusable integer primary key."""

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )


class TimestampMixin:
    """Automatically managed timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class SoftDeleteMixin:
    """Soft delete support."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

class PublicIdMixin:
    """Public identifier exposed through APIs."""

    public_id: Mapped[UUID] = mapped_column(
        Uuid,
        unique=True,
        nullable=False,
        index=True,
        default=generate_public_id,
    )

class ReferenceMixin:
    """Provides a standardized baseline for static or system lookup data tables."""
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)