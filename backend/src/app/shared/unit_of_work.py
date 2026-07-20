from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    """
    Lightweight transaction manager.

    Services own transactions.
    Repositories never commit directly.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()

    async def flush(self) -> None:
        await self.db.flush()

    async def refresh(self, entity) -> None:
        await self.db.refresh(entity)