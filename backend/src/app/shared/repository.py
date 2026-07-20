from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Generic async repository with common CRUD helpers.

    Feature-specific repositories should inherit from this class
    and implement only business-specific queries.
    """

    def __init__(
        self,
        db: AsyncSession,
        model: type[ModelType],
    ) -> None:
        self.db = db
        self.model = model

    async def get_by_id(
        self,
        entity_id: int,
    ) -> ModelType | None:
        result = await self.db.execute(
            select(self.model).where(self.model.id == entity_id)
        )

        return result.scalar_one_or_none()

    async def get_all(self) -> list[ModelType]:
        result = await self.db.execute(
            select(self.model)
        )

        return list(result.scalars().all())

    async def add(
        self,
        entity: ModelType,
    ) -> ModelType:
        self.db.add(entity)
        await self.db.flush()
        return entity

    async def delete(
        self,
        entity: ModelType,
    ) -> None:
        await self.db.delete(entity)
        await self.db.flush()

    async def exists(
        self,
        entity_id: int,
    ) -> bool:
        return await self.get_by_id(entity_id) is not None