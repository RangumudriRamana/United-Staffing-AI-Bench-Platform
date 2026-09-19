import asyncio

from app.auth.bootstrap import ensure_initial_admin
from app.database.session import SessionLocal


async def main() -> None:
    async with SessionLocal() as db:
        await ensure_initial_admin(db)


if __name__ == "__main__":
    asyncio.run(main())
