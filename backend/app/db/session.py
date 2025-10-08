from __future__ import annotations

from contextlib import asynccontextmanager

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from ..core.config import settings


engine: AsyncEngine = create_async_engine(settings.database_url, echo=False, future=True)


async def init_db() -> None:
    """Create all database tables."""

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
def get_session() -> AsyncSession:
    """Provide an async database session dependency."""

    async_session = AsyncSession(engine, expire_on_commit=False)
    try:
        yield async_session
    finally:
        await async_session.close()
