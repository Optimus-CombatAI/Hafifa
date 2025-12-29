import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import create_app
from db.database import Database
from settings import settings
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import create_app

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import create_app


@pytest.fixture(scope="function")
async def test_db():
    db = Database(db_url=settings.DB_URL, scheme=settings.MOCK_SCHEME)

    await db.create_tables()
    await db.reset_tables(drop_previous=True)

    yield db

    await db.reset_tables(drop_previous=True)
    await db.engine.dispose()


@pytest.fixture(scope="function")
async def client(test_db):
    app = create_app(app_db=test_db)

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as ac:
        yield ac
