from collections.abc import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

logger = structlog.get_logger(__name__)

engine = create_async_engine(
    settings.get_database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.SQLALCHEMY_ECHO,
    future=True,
)

AsyncSessionLocal = async_sessionmaker[AsyncSession](
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def init_db() -> None:
    """Initialize the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close the connection to the database."""
    await engine.dispose()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
            logger.debug("database_transaction_committed")
        except Exception as exc:
            await session.rollback()
            logger.error(
                "database_transaction_failed",
                exc_info=exc,
                error_type=type(exc).__name__,
            )
            raise
        finally:
            await session.close()
