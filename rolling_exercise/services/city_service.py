from sqlalchemy import select, exists, Select

from entities.city import City
from services.service import Service


def _get_existing_cities_stmt(city_name: str) -> Select:
    stmt = exists().where(
        City.name == city_name
    )
    final_stmt = select(stmt)

    return final_stmt


class CityService(Service):
    def __init__(self, db):
        super().__init__(db)

    async def is_existing_city(self, city_name: str) -> bool:
        stmt = _get_existing_cities_stmt(city_name)

        is_exist = await self.db.execute_with_scalar_results(stmt)

        return is_exist[0]
