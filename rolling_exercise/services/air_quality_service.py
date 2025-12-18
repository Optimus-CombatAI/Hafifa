from datetime import datetime
from typing import List

from fastapi import UploadFile
import logging
import numpy as np
import pandas as pd

from exceptions.notFullDataFileException import NotFullDataFileException
from exceptions.notValidDateException import NotValidDateException
from exceptions.notExistingCityException import NotExistingCityException
from utils.utils import fill_weather_report
from utils.utils import is_valid_date
from models.airQualityDataRow import AirQualityDataRow
import connectors.db_connector as db_connector
from utils.calculate_aqi import calculate_aqi
from settings import settings

logger = logging.getLogger(__name__)


async def upload_air_quality(file: UploadFile):
    data_df = pd.read_csv(file.file)

    if settings.USE_DATA_FILL:
        logger.info("used auto fill")
        fill_weather_report(data_df, settings.METHOD)

    else:
        if data_df.isnull().values.any():
            raise NotFullDataFileException

    check_colum_dates = np.vectorize(is_valid_date)

    if not check_colum_dates(data_df["date"]).all():
        raise NotValidDateException

    city_names_df = data_df[["city"]].drop_duplicates()
    await db_connector.insert_cities(city_names_df)

    report_data_df = data_df[["date", "city", "PM2.5", "NO2", "CO2"]]
    report_data_df = report_data_df.rename(columns={"city": "name"})

    calc_column_aqi = np.vectorize(calculate_aqi)
    report_data_df["overall_aqi"], report_data_df["aqi_level"] = calc_column_aqi(report_data_df["PM2.5"],
                                                                                 report_data_df["NO2"],
                                                                                 report_data_df["CO2"])

    await db_connector.insert_reports(report_data_df)

    logger.info(f"cities_inserted: {len(city_names_df)}\nreports_inserted: {len(report_data_df)}")


async def get_air_quality_by_time_range(start_date: str, end_date: str) -> List[AirQualityDataRow]:
    if not is_valid_date(start_date) or not is_valid_date(end_date):
        raise NotValidDateException

    start_date, end_date = datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d")

    return await db_connector.get_air_quality_by_time_range(start_date, end_date)


async def get_air_quality_by_city_name(city_name: str) -> List[AirQualityDataRow]:
    if not await db_connector.is_existing_city(city_name):
        raise NotExistingCityException

    return await db_connector.get_air_quality_by_city_name(city_name)
