from datetime import date
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(
    prefix="/air_quality",
    tags=["Air Quality"]
)


class Item(BaseModel):
    name: str
    description: Optional[str] = None


@router.post("/")
async def update_air_quality(item: Item):
    """
    This function adds to the database the weather data it receives
    :param item: a multipart/form-data request containing a CSV file.
    :return:
    """

    return {"air_quality": "good"}


@router.get("/by_time/")
async def get_air_quality_by_time_range(start_date: date, end_date: date):
    """
    This function gets the weather data within a range for all the cities
    :param start_date: initial date of the range
    :param end_date: final date of the range
    :return: the weather within the range for all the cities
    """

    return {"air_quality": f"from {start_date} to {end_date}"}


@router.get("/by_city/")
async def get_air_quality_by_city(city_name: str):
    """
    This function gets all the weather data for a given city
    :param city_name: the name of the city to get the weather from
    :return: all the weather in the city
    """

    return {"air_quality": f"from {city_name}"}


