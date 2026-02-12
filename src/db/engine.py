"""Async SQLAlchemy engine for Neon Postgres."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.get_env import env

_engine: AsyncEngine | None = None


def _normalize_url(url: str) -> str:
    """Ensure URL uses asyncpg driver prefix."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def get_engine() -> AsyncEngine:
    """Get or create the async engine singleton."""
    global _engine
    if _engine is None:
        url = _normalize_url(env("PRJ_NEON_DATABASE_URL"))
        _engine = create_async_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=600,
            pool_size=5,
            max_overflow=2,
        )
    return _engine


def get_session_factory() -> sessionmaker:
    """Get an async session factory bound to the engine."""
    return sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def dispose_engine() -> None:
    """Dispose the engine and reset the singleton."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
