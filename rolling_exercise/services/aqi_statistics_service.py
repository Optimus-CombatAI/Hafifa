
from typing import List

from exceptions.notExistingCityException import NotExistingCityException
from models.AQIDataRow import AQIDataRow
import connectors.db_connector as db_connector


async def get_aqi_history_by_city(city_name: str) -> List[AQIDataRow]:
    if not await db_connector.is_existing_city(city_name):
        raise NotExistingCityException

    aqi_data_rows = await db_connector.get_aqi_history_by_city(city_name)

    return aqi_data_rows


async def get_aqi_avg_by_city(city_name: str) -> AQIDataRow:
    if not await db_connector.is_existing_city(city_name):
        raise NotExistingCityException

    aqi_data_row = await db_connector.get_aqi_avg_by_city(city_name)

    return aqi_data_row


async def get_3_best_cities() -> List[str]:
    return await db_connector.get_3_best_cities()
