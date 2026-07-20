from sqlalchemy import Boolean, String, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.auth.enums import Role

from app.database.base import Base

from app.database.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
    PublicIdMixin,
)

class User(
    PrimaryKeyMixin,
    PublicIdMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(String(255))

    first_name: Mapped[str] = mapped_column(String(100))

    last_name: Mapped[str] = mapped_column(String(100))

    role: Mapped[Role] = mapped_column(
        SqlEnum(
            Role,
            name="user_role",
            native_enum=True,
        ),
        nullable=False,
        default=Role.BENCH_SALES_RECRUITER,
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )