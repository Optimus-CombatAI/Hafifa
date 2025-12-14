from fastapi import APIRouter, HTTPException
from datetime import datetime

from entities.alertReturnRow import AlertReturnRow
import db.db_functions as db_funcs
from utils.utils import is_valid_date

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


@router.get("/")
async def get_all_alerts_handler() -> list[AlertReturnRow]:
    """
    This function returns all the recorded alerts
    :return: all the recorded alerts
    """
    alerts = await db_funcs.get_all_alerts()

    if not alerts:
        raise HTTPException(status_code=404, detail=f"No alerts found")

    return alerts


@router.get("/since")
async def get_alerts_by_date_handler(start_date: str) -> list[AlertReturnRow]:
    """
    This function returns all the recorded alerts that happened during the day
    :param start_date: the date of the day to get the alerts from
    :return: recorded alerts that happened during the day
    """
    if not is_valid_date(start_date):
        raise HTTPException(status_code=422, detail="Dates not in format YYYY-MM-DD or not valid")

    start_date = datetime.strptime(start_date, "%Y-%m-%d")

    alerts_from_start_date = await db_funcs.get_alerts_since_date(start_date)

    if not alerts_from_start_date:
        raise HTTPException(status_code=404, detail=f"No alerts found")

    return alerts_from_start_date


@router.get("/by_city")
async def get_alerts_by_city_handler(city_name: str) -> list[AlertReturnRow]:
    """
    This function returns all the recorded alerts that happened in the city
    :param city_name: the name of the city to get the alerts from
    :return: recorded alerts that happened in the city
    """

    alerts_from_city = await db_funcs.get_alerts_from_city(city_name)

    if not alerts_from_city:
        raise HTTPException(status_code=404, detail=f"No alerts found")

    return alerts_from_city

