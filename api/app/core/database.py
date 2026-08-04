"""
Synkora API — Database Engine & Session

Configures the async SQLAlchemy engine and provides a session factory.
Uses asyncpg as the async driver for PostgreSQL.

For development without PostgreSQL, falls back to SQLite (aiosqlite).
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("database")


def _get_database_url() -> str:
    """
    Returns the database URL, converting to async driver if needed.
    Falls back to SQLite for local development without PostgreSQL.
    """
    url = settings.DATABASE_URL

    # If the URL starts with "sqlite", use aiosqlite driver
    if url.startswith("sqlite"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    # Ensure async PostgreSQL driver
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)

    return url


database_url = _get_database_url()

# ── Async Engine ────────────────────────────────────────────────────────
engine = create_async_engine(
    database_url,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    # PostgreSQL-specific pool settings
    **(
        {
            "pool_size": 20,
            "max_overflow": 10,
            "pool_recycle": 3600,
        }
        if "postgresql" in database_url
        else {}
    ),
)

# ── Session Factory ─────────────────────────────────────────────────────
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    FastAPI dependency that yields an async database session.
    Automatically commits on success or rolls back on error.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize the database — create all tables.
    Called once at application startup.
    """
    from app.models import Base  # noqa: F811

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("database_initialized", url=database_url.split("@")[-1] if "@" in database_url else database_url)


async def close_db() -> None:
    """Dispose of the engine connection pool on shutdown."""
    await engine.dispose()
    logger.info("database_closed")
