from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import PrimaryKeyMixin, PublicIdMixin, TimestampMixin


class AuthSession(
    PrimaryKeyMixin,
    PublicIdMixin,
    TimestampMixin,
    Base,
):
    """
    Server-side authentication session record.

    Stores the JWT identifier and allows individual tokens
    to be revoked during logout.
    """

    __tablename__ = "auth_sessions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    jti: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        index=True,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )