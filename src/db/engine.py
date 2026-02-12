"""Async SQLAlchemy engine for Neon Postgres.

depends_on:
  - src/get_env.py
depended_by:
  - src/db/crud.py
  - src/db/__init__.py
  - src/hooks/activity_tracker.py
semver: major
"""

from __future__ import annotations

import ssl
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.get_env import env

_engine: AsyncEngine | None = None


def _normalize_url(url: str) -> str:
    """Ensure URL uses asyncpg driver prefix and strip sslmode (asyncpg incompatible)."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # Strip sslmode/channel_binding — asyncpg doesn't support them as URL params
    parts = urlsplit(url)
    if parts.query:
        params = parse_qs(parts.query)
        params.pop("sslmode", None)
        params.pop("channel_binding", None)
        url = urlunsplit(parts._replace(query=urlencode(params, doseq=True)))
    return url


def get_engine() -> AsyncEngine:
    """Get or create the async engine singleton."""
    global _engine
    if _engine is None:
        url = _normalize_url(env("PRJ_NEON_DATABASE_URL"))
        # Neon requires SSL — create a default SSL context for asyncpg
        ssl_context = ssl.create_default_context()
        _engine = create_async_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=600,
            pool_size=5,
            max_overflow=2,
            connect_args={"ssl": ssl_context},
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
