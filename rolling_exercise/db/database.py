
import logging

from contextlib import asynccontextmanager
from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from settings import settings

Base = declarative_base()
metadata = MetaData()

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(
            db_url,
            connect_args={"server_settings": {"search_path": settings.SCHEME}},
            pool_pre_ping=True,
            pool_recycle=1800,
            echo=False,
        )
        self.metadata = metadata

        self._session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        self.retries = settings.DEFAULT_RETRIES
        self.delay = settings.DEFAULT_DELAY

    async def create_tables(self) -> None:
        async with self.engine.begin() as conn:  # async connection context
            await conn.run_sync(self.metadata.create_all)

    async def reset_tables(self, drop_previous=False):
        if drop_previous:
            async with self.engine.begin() as conn:
                for table in reversed(self.metadata.sorted_tables):
                    await conn.execute(text(f'DROP TABLE IF EXISTS "{table.name}" CASCADE;'))

            await self.engine.run_sync(self.metadata.create_all)

    @asynccontextmanager
    async def session(self):
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()

            except Exception as e:
                await session.rollback()
                logger.exception(f"rolled back\n{str(e)}")
                raise
            finally:
                logger.info("session closed")


db = Database(settings.DB_URL)
