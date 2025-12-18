
from fastapi import APIRouter, HTTPException

from exceptions.notValidDateException import NotValidDateException
from exceptions.notExistingCityException import NotExistingCityException
from models.alertReturnRow import AlertReturnRow
import services.alerts_service as alerts_service

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
    return await alerts_service.get_all_alerts()


@router.get("/since")
async def get_alerts_since_date_handler(start_date: str) -> list[AlertReturnRow]:
    """
    This function returns all the recorded alerts that happened during the day
    :param start_date: the date of the day to get the alerts from
    :return: recorded alerts that happened during the day
    """

    try:
        alerts_since_start_date = await alerts_service.get_alerts_since_date(start_date)

    except NotValidDateException as e:
        raise HTTPException(status_code=400, detail=e.message)

    return alerts_since_start_date


@router.get("/by_city")
async def get_alerts_by_city_handler(city_name: str) -> list[AlertReturnRow]:
    """
    This function returns all the recorded alerts that happened in the city
    :param city_name: the name of the city to get the alerts from
    :return: recorded alerts that happened in the city
    """

    try:
        alerts_from_city = await alerts_service.get_alerts_by_city(city_name)

    except NotExistingCityException as e:
        raise HTTPException(status_code=404, detail=e.message)

    return alerts_from_city
