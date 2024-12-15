import sqlalchemy

from sqlalchemy.orm import sessionmaker
from rolling_exercise.config import settings

engine = sqlalchemy.create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
