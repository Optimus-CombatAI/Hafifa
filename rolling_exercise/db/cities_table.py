from sqlalchemy import Table, Column, Integer, String, MetaData


def _define_cities_table(metadata: MetaData) -> Table:
    cities = Table(
        'cities', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String, unique=True, nullable=False),
    )

    return cities
