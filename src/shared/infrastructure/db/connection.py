import os
from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def _build_async_db_url() -> str:
    def _normalize(value: str | None, default: str) -> str:
        if not value:
            return default
        v = value.strip()
        if v.lower() in {"none", "null"}:
            return default
        return v

    db_name = _normalize(os.getenv("POSTGRES_DB"), "")
    db_user = _normalize(os.getenv("POSTGRES_USER"), "")
    db_password = _normalize(os.getenv("POSTGRES_PASSWORD"), "")
    db_host = _normalize(os.getenv("POSTGRES_HOST"), "localhost")
    db_port = _normalize(os.getenv("POSTGRES_PORT"), "5432")

    return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


@lru_cache(maxsize=1)
def get_async_engine() -> AsyncEngine:
    """
    Create (lazy) and cache `AsyncEngine` globally for the application.
    """
    database_url = _build_async_db_url()
    engine = create_async_engine(
        database_url,
        pool_pre_ping=True,
    )
    return engine


@lru_cache(maxsize=1)
def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Return async session factory (AsyncSessionLocal) for the application.
    """
    engine = get_async_engine()
    return async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    )


def get_async_session() -> AsyncSession:
    """
    Get new SQLAlchemy AsyncSession.

    Example:
        from src.shared.infrastructure.db.connection import get_async_session
        from sqlalchemy import text

        async def main():
            async_session = get_async_session()
            async with async_session as db:
                result = await db.execute(text("SELECT 1"))
                print(result.scalar_one())
    """
    AsyncSessionLocal = get_async_session_factory()
    return AsyncSessionLocal()


async def async_session_scope() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager generator for using AsyncSession safely.

    Example:
        from src.shared.infrastructure.db.connection import async_session_scope
        from sqlalchemy import text

        async def main():
            async for db in async_session_scope():
                result = await db.execute(text("SELECT 1"))
                print(result.scalar_one())
    """
    async_session = get_async_session()
    async with async_session as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise
