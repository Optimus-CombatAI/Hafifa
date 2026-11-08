from collections.abc import Iterator

import pytest
from sqlalchemy.orm import Session

from src.db.database import create_session_factory

IN_MEMORY_SQLITE_URL = "sqlite://"


@pytest.fixture
def session() -> Iterator[Session]:
    with create_session_factory(IN_MEMORY_SQLITE_URL)() as session:
        yield session
