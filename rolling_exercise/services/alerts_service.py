
from datetime import datetime
from typing import List

from exceptions.notExistingCityException import NotExistingCityException
from exceptions.notValidDateException import NotValidDateException
from models.alertReturnRow import AlertReturnRow
import connectors.db_connector as db_connector
from utils.utils import is_valid_date


async def get_all_alerts() -> List[AlertReturnRow]:
    return await db_connector.get_all_alerts()


async def get_alerts_since_date(start_date: str) -> List[AlertReturnRow]:

    if not is_valid_date(start_date):
        raise NotValidDateException

    start_date = datetime.strptime(start_date, "%Y-%m-%d")

    alert_return_rows = await db_connector.get_alerts_since_date(start_date)

    return alert_return_rows


async def get_alerts_by_city(city_name) -> List[AlertReturnRow]:

    if not await db_connector.is_existing_city(city_name):
        raise NotExistingCityException

    return await db_connector.get_alerts_by_city(city_name)
