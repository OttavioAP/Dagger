from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator, Optional
from functools import lru_cache
import logging
from fastapi import HTTPException, Header, status
from app.utils.database_utils import create_database_config
from app.config.config import app_settings

Base = declarative_base()

logger = logging.getLogger(__name__)


class DatabaseService:
    _instance: Optional["DatabaseService"] = None

    def __init__(self):
        # Get database configuration for local Postgres
        db_config = create_database_config()
        logger.info(
            f"Initializing database connection to: {db_config.connection_string}"
        )

        self.engine = create_async_engine(
            db_config.connection_string, **db_config.options
        )
        logger.info("Database engine created successfully")

        self.AsyncSessionLocal = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def init_db(self):
        """Initialize database with tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def dispose(self):
        """Cleanup database connections"""
        if self.engine:
            await self.engine.dispose()

    @classmethod
    def get_instance(cls) -> "DatabaseService":
        if not cls._instance:
            cls._instance = DatabaseService()
        return cls._instance


# Dependency to get DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db_service = get_database_service()
    async for session in db_service.get_session():
        yield session


@lru_cache()
def get_database_service() -> DatabaseService:
    return DatabaseService.get_instance()
