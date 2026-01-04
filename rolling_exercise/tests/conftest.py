import pytest
from httpx import AsyncClient, ASGITransport

from db.pgDatabase import PGDatabase
from consts import settings
from app.main import create_app


@pytest.fixture(scope="function")
async def test_db():
    db = PGDatabase(db_url=settings.DB_URL, scheme=settings.SCHEME)

    await db.create_tables()
    await db.reset_tables(drop_previous=True)

    yield db

    await db.reset_tables(drop_previous=True)
    await db.engine.dispose()


@pytest.fixture(scope="function")
async def client(test_db) -> AsyncClient:
    app = create_app(app_db=test_db)

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as ac:
        yield ac
