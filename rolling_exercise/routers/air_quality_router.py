
from fastapi import APIRouter, HTTPException, UploadFile, status
from starlette.responses import Response

from models.airQualityDataRow import AirQualityDataRow
from exceptions.notValidDateException import NotValidDateException
from exceptions.notExistingCityException import NotExistingCityException
from exceptions.dbIntegrityException import DBIntegrityException
from services import air_quality_service

router = APIRouter(
    prefix="/air_quality",
    tags=["Air Quality"]
)


@router.post("/upload")
async def upload_air_quality_handler(file: UploadFile) -> Response:
    """
    This function adds to the database the weather data it receives and alerts if there are
    :param file: a multipart/form-data request containing a CSV file.
    :return: a response if created successfully
    """

    try:
        await air_quality_service.upload_air_quality(file)

    except DBIntegrityException as e:
        raise HTTPException(status_code=400, detail=e.message)

    return Response(status_code=status.HTTP_201_CREATED)


@router.get("/by_time")
async def get_air_quality_by_time_range_handler(start_date: str, end_date: str) -> list[AirQualityDataRow]:
    """
    This function gets the weather data within a range for all the cities
    :param start_date: initial date of the range
    :param end_date: final date of the range
    :return: the weather within the range for all the cities
    """

    try:
        air_quality_data_rows = await air_quality_service.get_air_quality_by_time_range(start_date, end_date)

    except NotValidDateException as e:
        raise HTTPException(status_code=400, detail=e.message)

    return air_quality_data_rows


@router.get("/by_city")
async def get_air_quality_by_city_handler(city_name: str) -> list[AirQualityDataRow]:
    """
    This function gets all the weather data for a given city
    :param city_name: the name of the city to get the weather from
    :return: all the weather in the city
    """

    try:
        air_quality_data_rows = await air_quality_service.get_air_quality_by_city_name(city_name)

    except NotExistingCityException as e:
        raise HTTPException(status_code=404, detail=e.message)

    return air_quality_data_rows
