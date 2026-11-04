from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.db.base import Base


def create_session_factory(database_url: str) -> sessionmaker[Session]:
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)

    return sessionmaker(engine)
