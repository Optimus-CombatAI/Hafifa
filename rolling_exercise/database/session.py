import sqlalchemy
from ..config import settings

engine = sqlalchemy.create_engine(settings.DATABASE_URL)
SessionLocal = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
