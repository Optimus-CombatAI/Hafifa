from sqlalchemy import Table, Column, Integer, String
from db.database import metadata

cities = Table(
    'cities', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, unique=True, nullable=False),
)
