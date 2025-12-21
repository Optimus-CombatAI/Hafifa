from sqlalchemy import select, exists, Select

from db.database import db
from entities.city import City


def _get_existing_cities_stmt(city_name: str) -> Select:
    stmt = exists().where(
        City.name == city_name
    )
    final_stmt = select(stmt)

    return final_stmt


async def is_existing_city(city_name: str) -> bool:
    stmt = _get_existing_cities_stmt(city_name)

    is_exist = await db.execute_with_scalar_results(stmt)

    return is_exist[0]
