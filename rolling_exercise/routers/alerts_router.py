from fastapi import APIRouter
from datetime import date

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


@router.get("/")
async def get_all_alerts():
    """
    This function returns all the recorded alerts
    :return: all the recorded alerts
    """
    return {"air_quality": f"... "}


@router.get("/by_date")
async def get_alerts_by_date(day_date: date):
    """
    This function returns all the recorded alerts that happened during the day
    :param day_date: the date of the day to get the alerts from
    :return: recorded alerts that happened during the day
    """

    return {"air_quality": f"from {day_date}"}


@router.get("/by_city")
async def get_alerts_by_city(city_name: str):
    """
    This function returns all the recorded alerts that happened in the city
    :param city_name: the name of the city to get the alerts from
    :return: recorded alerts that happened in the city
    """
    return {"air_quality": f"from {city_name}"}
