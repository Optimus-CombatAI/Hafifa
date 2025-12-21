
from datetime import datetime, timedelta
import random

import logging
from sqlalchemy.dialects.postgresql import insert

from db.database import db
from db.cities_table import cities
from db.reports_table import reports


logger = logging.getLogger(__name__)


def _get_random_date(start: datetime = datetime(2025, 11, 10),
                     end: datetime = datetime(2025, 11, 15)) -> datetime.date:
    delta = end - start
    random_days = random.randint(0, delta.days)

    return (start + timedelta(days=random_days)).date()


async def fill_dummy_data(use_dummy_dataset=False) -> None:
    if use_dummy_dataset:
        random_cities = ['Be\'er Sheva', 'Holon', 'Haifa', 'Tel Aviv', 'Netanya']
        levels = ["Good", "Moderate", "Unhealthy for Sensitive Groups", "Unhealthy", "Very Unhealthy", "Hazardous"]
        city_stmt = [insert(cities).values(name=city_name) for city_name in random_cities]
        report_stmt = []

        for i in range(5):
            report_stmt.append(
                insert(reports).values(date=_get_random_date(), city_id=random.randint(1, len(random_cities)),
                                       pm2_5=random.randint(1, 10), no2=random.randint(1, 10),
                                       co2=random.randint(1, 10),
                                       overall_aqi=random.randint(1, 10), aqi_level=random.choice(levels))
            )

        async with db.engine.begin() as conn:
            for stmt in city_stmt:
                await conn.execute(stmt)
            for stmt in report_stmt:
                await conn.execute(stmt)

            logger.info("Inserted successfully with Core.")
