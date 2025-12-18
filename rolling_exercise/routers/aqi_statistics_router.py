from fastapi import APIRouter, HTTPException

from exceptions.notExistingCityException import NotExistingCityException
from models.AQIDataRow import AQIDataRow
import services.aqi_statistics_service as aqi_statistics_service

router = APIRouter(
    prefix="/aqi_statistics",
    tags=["AQI Statistics"]
)


@router.get("/history")
async def get_aqi_history_by_city_handler(city_name: str) -> list[AQIDataRow]:
    """
    This function return the aqi history of a given city
    :param city_name: the name of the city to get history of aqi
    :return: aqi history of the given city
    """

    try:
        aqi_city_history = await aqi_statistics_service.get_aqi_history_by_city(city_name)

    except NotExistingCityException as e:
        raise HTTPException(status_code=404, detail=e.message)

    return aqi_city_history


@router.get("/average")
async def get_avg_aqi_by_city_handler(city_name: str) -> AQIDataRow:
    """
    This function returns the average aqi score for a given city
    :param city_name: the name of the city to calculate the average aqi
    :return: the average aqi score
    """

    try:
        aqi_city_avg = await aqi_statistics_service.get_aqi_avg_by_city(city_name)

    except NotExistingCityException as e:
        raise HTTPException(status_code=404, detail=e.message)

    return aqi_city_avg


@router.get("/best_cities")
async def get_aqi_best_cities_handler() -> list[str]:
    """
    This function returns 3 cities with the best aqi score(the lowest score)
    :return: 3 cities with lowest aqi
    """

    return await aqi_statistics_service.get_3_best_cities()
