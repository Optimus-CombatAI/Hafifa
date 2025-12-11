from sqlalchemy import Table, Column, Integer, String
from consts import META_DATA

cities = Table(
    'cities', META_DATA,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, unique=True),
)
