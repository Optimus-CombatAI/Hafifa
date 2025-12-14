from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, status
from pydantic import BaseModel
from starlette.responses import Response

import db.db_functions as db_funcs
from consts import METHOD, LOGGER, USE_DATA_FILL
from entities.airQualityDataRow import AirQualityDataRow
from entities.duplicateDataException import DuplicateDataException
from utils.utils import is_valid_date, fill_weather_report

router = APIRouter(
    prefix="/air_quality",
    tags=["Air Quality"]
)


class Item(BaseModel):
    name: str
    description: Optional[str] = None


@router.post("/upload")
async def upload_air_quality_handler(file: UploadFile) -> Response:
    """
    This function adds to the database the weather data it receives and alerts if there are
    :param file: a multipart/form-data request containing a CSV file.
    :return: a response if created successfully
    """
    data_df = pd.read_csv(file.file)

    if USE_DATA_FILL:
        LOGGER.info("used auto fill")
        fill_weather_report(data_df, METHOD)
    else:
        if data_df.isnull().values.any():
            raise HTTPException(status_code=400, detail="Make sure the file is full and there are no empty cells")

    vectorized_check = np.vectorize(is_valid_date)
    if not vectorized_check(data_df["date"]).all():
        raise HTTPException(status_code=400, detail="Make sure the dates are in the right format")

    city_names_df = data_df[["city"]].drop_duplicates()
    await db_funcs.insert_cities(city_names_df)

    report_data_df = data_df[["date", "city", "PM2.5", "NO2", "CO2"]]
    try:
        await db_funcs.insert_reports(report_data_df)

    except DuplicateDataException as duplicate_data_exception:
        raise HTTPException(status_code=400, detail=str(duplicate_data_exception))

    LOGGER.info(f"cities_inserted: {len(city_names_df)}\nreports_inserted: {len(report_data_df)}")

    return Response(status_code=status.HTTP_201_CREATED)


@router.get("/by_time")
async def get_air_quality_by_time_range_handler(start_date: str, end_date: str) -> list[AirQualityDataRow]:
    """
    This function gets the weather data within a range for all the cities
    :param start_date: initial date of the range
    :param end_date: final date of the range
    :return: the weather within the range for all the cities
    """

    if not is_valid_date(start_date) or not is_valid_date(end_date):
        raise HTTPException(status_code=422, detail="Dates not in format YYYY-MM-DD or not valid")

    start_date, end_date = datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d")

    aqi_list = await db_funcs.get_air_quality_by_time_range(start_date, end_date)

    if not aqi_list:
        raise HTTPException(status_code=404, detail="No AQI data for this time range")

    return aqi_list


@router.get("/by_city")
async def get_air_quality_by_city_handler(city_name: str) -> list[AirQualityDataRow]:
    """
    This function gets all the weather data for a given city
    :param city_name: the name of the city to get the weather from
    :return: all the weather in the city
    """

    aqi_list = await db_funcs.get_air_quality_by_city_name(city_name)

    if not aqi_list:
        raise HTTPException(status_code=404, detail=f"No AQI data for the city {city_name}")

    return aqi_list
