from fastapi import APIRouter, HTTPException

import db.db_functions as db_funcs
from entities.AQIDataRow import AQIDataRow


router = APIRouter(
    prefix="/aqi_statistics",
    tags=["AQI Statistics"]
)


@router.get("/history")
async def get_aqi_history_by_city(city_name: str) -> list[AQIDataRow]:
    """
    This function return the aqi history of a given city
    :param city_name: the name of the city to get history of aqi
    :return: aqi history of the given city
    """

    aqi_city_history = await db_funcs.get_aqi_history_by_city(city_name)

    if not aqi_city_history:
        raise HTTPException(status_code=404, detail=f"No AQI history for the city {city_name}")

    return aqi_city_history


@router.get("/average")
async def get_avg_aqi_by_city(city_name: str) -> AQIDataRow:
    """
    This function returns the average aqi score for a given city
    :param city_name: the name of the city to calculate the average aqi
    :return: the average aqi score
    """

    aqi_city_avg = await db_funcs.get_aqi_avg_by_city(city_name)

    if aqi_city_avg.overall_aqi == -1:
        raise HTTPException(status_code=404, detail=f"No AQI history for the city {city_name}")

    return aqi_city_avg


@router.get("/best_cities")
async def get_aqi_best_cities() -> list[str]:
    """
    This function returns 3 cities with the best aqi score(the lowest score)
    :return: 3 cities with lowest aqi
    """

    best_cities = await db_funcs.get_3_best_cities()

    if not best_cities:
        raise HTTPException(status_code=404, detail=f"No AQI history for the cities")

    return best_cities
