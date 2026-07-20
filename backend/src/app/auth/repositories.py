from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.shared.repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Database access layer for users.
    """

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, User)

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()

    async def get_by_public_id(
        self,
        public_id: UUID,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(
                User.public_id == public_id
            )
        )

        return result.scalar_one_or_none()