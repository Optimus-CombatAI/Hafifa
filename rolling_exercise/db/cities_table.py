from sqlalchemy import Table, Column, Integer, String

from db.database import Database


def _define_cities_table(db: Database) -> Table:
    cities = Table(
        'cities', db.metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String, unique=True, nullable=False),
    )

    return cities
