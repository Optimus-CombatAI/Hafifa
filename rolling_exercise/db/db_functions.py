from datetime import datetime, timedelta
import random

from sqlalchemy import Table, Column, Integer, String, Date, ForeignKey, text, insert, select

from consts import ENGINE, LOGGER, META_DATA, SESSION
from entities.city import City
from entities.report import Report


cities = Table(
    'cities', META_DATA,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String),
)

reports = Table(
    'reports', META_DATA,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('date', Date),
    Column('city_id', Integer, ForeignKey('cities.id', ondelete='CASCADE')),
    Column('pm2_5', Integer),
    Column('no2', Integer),
    Column('co2', Integer),
    Column('aqi', Integer),
)


async def set_up_db():
    with ENGINE.connect() as conn:
        for table in reversed(META_DATA.sorted_tables):
            conn.execute(text(f"DROP TABLE IF EXISTS {table.name} CASCADE;"))

        conn.commit()

    META_DATA.create_all(ENGINE)


def _get_random_date(start: datetime = datetime(2025, 11, 10), end: datetime = datetime(2025, 11, 15)) -> datetime.date:
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).date()


async def fill_dummy_data():
    random_cities = ['Be\'er Sheva', 'Holon', 'Haifa', 'Tel Aviv', 'Netanya']
    city_stmt = [insert(cities).values(name=city_name) for city_name in random_cities]

    report_stmt = []
    for i in range(5):
        report_stmt.append(
            insert(reports).values(date=_get_random_date(), city_id=random.randint(1, len(random_cities)),
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


def close_session():
    SESSION.close()


async def get_air_quality_by_time_range(start_date: datetime.date, end_date: datetime.date):
    stmt = (
        select(City.id, City.name, Report.date)
        .select_from(City)
        .join(Report, City.id == Report.city_id)
        .where(
            (Report.date >= start_date) &
            (Report.date <= end_date)
        )
    )

    results = SESSION.execute(stmt).mappings().all()
    return results


if __name__ == '__main__':
    set_up_db()
