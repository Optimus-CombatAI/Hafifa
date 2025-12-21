
from sqlalchemy import select, Select
from sqlalchemy.orm import joinedload

from db.database import db
from entities.city import City
from entities.report import Report


def _get_existing_cities_stmt(city_name: str) -> Select:
    stmt = (
        select(Report)
        .options(joinedload(Report.city))
        .where(
            Report.city.has(City.name == city_name)
        )
    )

    return stmt


async def is_existing_city(city_name) -> bool:

    stmt = _get_existing_cities_stmt(city_name)

    reports_results = await db.execute_with_scalar_results(stmt)

    return len(reports_results) != 0
