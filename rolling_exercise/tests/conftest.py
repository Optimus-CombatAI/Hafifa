import asyncio
import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

load_dotenv(".env.test", override=True)

from app.constants.config import settings
from app.db.session import Base
from app.main import app as fastapi_app



@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) :
    SessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)

    async with SessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def clean_db(test_engine):
    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE air_quality_measurements RESTART IDENTITY;"))
    yield


@pytest_asyncio.fixture
async def client(test_engine):
    from app.db.session import get_db

    SessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)

    async def override_get_db():
        async with SessionLocal() as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    fastapi_app.dependency_overrides.clear()
