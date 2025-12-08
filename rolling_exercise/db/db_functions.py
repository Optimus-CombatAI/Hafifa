from datetime import datetime, timedelta
import random

from sqlalchemy import Table, Column, Integer, String, ForeignKey, text, insert
from consts import ENGINE, LOGGER, META_DATA

cities = Table(
    'cities', META_DATA,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String),
)

reports = Table(
    'reports', META_DATA,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('date', String),
    Column('city_id', Integer, ForeignKey('cities.id', ondelete='CASCADE')),
    Column('pm2_5', Integer),
    Column('no2', Integer),
    Column('co2', Integer),
    Column('aqi', Integer),
)


def set_up_db():
    with ENGINE.connect() as conn:
        for table in reversed(META_DATA.sorted_tables):
            conn.execute(text(f"DROP TABLE IF EXISTS {table.name} CASCADE;"))

        conn.commit()

    META_DATA.create_all(ENGINE)


def get_random_date(start: datetime = datetime(2020, 1, 1), end: datetime = datetime(2023, 12, 31)) -> datetime.date:
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).date()


def fill_dummy_data():
    random_cities = ['Be\'er Sheva', 'Holon', 'Haifa', 'Tel Aviv', 'Netanya']
    city_stmt = [insert(cities).values(name=city_name) for city_name in random_cities]

    report_stmt = []
    for i in range(5):
        report_stmt.append(
            insert(reports).values(date=get_random_date(), city_id=random.randint(1, len(random_cities)),
                                   pm2_5=random.randint(1, 10), no2=random.randint(1, 10), co2=random.randint(1, 10),
                                   aqi=random.randint(1, 10))
        )

    with ENGINE.connect() as connection:
        for stmt in city_stmt:
            connection.execute(stmt)

        for stmt in report_stmt:
            connection.execute(stmt)

        connection.commit()
        LOGGER.info("Inserted successfully with Core.")


if __name__ == '__main__':
    set_up_db()
