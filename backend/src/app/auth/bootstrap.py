from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.enums import Role
from app.auth.passwords import hash_password
from app.core.config import get_settings
from app.models.user import User


async def ensure_initial_admin(db: AsyncSession) -> None:
    """
    Creates the initial ADMIN user if no ADMIN exists.
    Safe to call on every application startup.
    """

    settings = get_settings()

    result = await db.execute(
        select(User).where(User.role == Role.ADMIN)
    )

    admin = result.scalar_one_or_none()

    if admin:
        print("Initial admin already exists.")
        return

    admin = User(
        email=settings.initial_admin_email,
        hashed_password=hash_password(settings.initial_admin_password),
        first_name=settings.initial_admin_first_name,
        last_name=settings.initial_admin_last_name,
        role=Role.ADMIN,
        is_active=True,
    )

    db.add(admin)
    await db.commit()

    print("✅ Initial ADMIN created successfully.")