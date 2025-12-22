from datetime import datetime
from typing import List, Dict, Any
import re

from fastapi import UploadFile
import logging
import numpy as np
import pandas as pd

from db.database import db
from entities.city import City
from entities.report import Report
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql import Select
from exceptions.dbDuplicationError import DBDuplicationError
from exceptions.duplicateReportForCityException import DuplicateReportForCity
from exceptions.notFullDataFileException import NotFullDataFileException
from exceptions.notExistingCityException import NotExistingCityException
from exceptions.notValidDateException import NotValidDateException
from models.airQualityDataRow import AirQualityDataRow
from services import city_service
from settings import settings
from utils import utils
from utils.calculate_aqi import calculate_aqi

logger = logging.getLogger(__name__)


def _validate_fullness(data_df: pd.DataFrame) -> None:
    if settings.USE_DATA_FILL:
        logger.info("used auto fill")
        utils.fill_weather_report(data_df, settings.METHOD)

    else:
        if data_df.isnull().values.any():
            raise NotFullDataFileException


def _validate_date_column(dates_column: pd.Series) -> None:
    check_column_dates = np.vectorize(utils.is_valid_date)

    if not check_column_dates(dates_column).all():
        raise NotValidDateException


def _validate_file_correctness(data_df: pd.DataFrame) -> None:
    _validate_fullness(data_df)
    _validate_date_column(data_df["date"])


def _fill_aqi_data(report_data_df: pd.DataFrame) -> None:
    calc_column_aqi = np.vectorize(calculate_aqi)
    report_data_df["overall_aqi"], report_data_df["aqi_level"] = calc_column_aqi(report_data_df["PM2.5"],
                                                                                 report_data_df["NO2"],
                                                                                 report_data_df["CO2"])


async def _insert_cities(city_names_df: pd.DataFrame) -> None:
    city_names_df = city_names_df.rename(columns={"city": "name"})

    stmt = insert(City).values(city_names_df.to_dict(orient="records"))
    stmt = stmt.on_conflict_do_nothing(index_elements=["name"])

    await db.execute_with_no_results(stmt)

    logger.info(f"cities_inserted: {len(city_names_df)}")


async def _get_cities_to_id_map() -> Dict[str, str]:
    result = await db.execute_with_plain_results(select(City.id, City.name))
    existing_cities = result.mappings().all()
    existing_map = {row["name"]: row["id"] for row in existing_cities}

    return existing_map


async def _create_report_from_row(report_row: pd.Series) -> Dict[str, Any]:

    city_name_to_id_map = await _get_cities_to_id_map()
    city_id = int(city_name_to_id_map.get(report_row["name"]))

    report = {
        "date": datetime.strptime(report_row["date"], settings.DATE_FORMAT),
        "city_id": city_id,
        "pm2_5": int(report_row["PM2.5"]),
        "no2": int(report_row["NO2"]),
        "co2": int(report_row["CO2"]),
        "overall_aqi": int(report_row["overall_aqi"]),
        "aqi_level": report_row["aqi_level"]
    }

    return report


async def _get_reports_statements(reports_df: pd.DataFrame) -> Insert:
    reports_to_insert = []

    for _, row in reports_df.iterrows():
        reports_to_insert.append(await _create_report_from_row(row))

    stmt = insert(Report).values(reports_to_insert)

    return stmt


async def _extract_city_name_and_date(error_message: str) -> tuple[str, datetime.date]:

    pattern = r"\((\d{4}-\d{2}-\d{2}),\s*(\d+)\)"
    match = re.search(pattern, error_message)

    date = datetime.strptime(match.group(1), settings.DATE_FORMAT).date()
    city_id = int(match.group(2))

    name_to_id_map = await _get_cities_to_id_map()
    city_name = next((k for k, v in name_to_id_map.items() if v == city_id), None)

    return city_name, date


async def _insert_reports(reports_df: pd.DataFrame) -> None:

    logger.info(reports_df)

    reports_stmts = await _get_reports_statements(reports_df)

    try:
        await db.execute_with_no_results(reports_stmts)

    except DBDuplicationError as e:
        city_name, date = await _extract_city_name_and_date(e.message)
        raise DuplicateReportForCity(city_name, date)

    logger.info(f"reports_inserted: {len(reports_df)}")


async def upload_air_quality(file: UploadFile) -> None:
    data_df = pd.read_csv(file.file)

    _validate_file_correctness(data_df)

    city_names_df = data_df[["city"]].drop_duplicates()
    await _insert_cities(city_names_df)

    report_data_df = data_df[["date", "city", "PM2.5", "NO2", "CO2"]].rename(columns={"city": "name"})
    _fill_aqi_data(report_data_df)
    await _insert_reports(report_data_df)


def _get_air_quality_time_range_stmt(start_date: datetime.date, end_date: datetime.date) -> Select:
    stmt = (
        select(Report)
        .options(joinedload(Report.city))
        .where(
            Report.date.between(start_date, end_date)
        )
    )

    return stmt


def _get_air_quality_city_stmt(city_name: str) -> Select:
    stmt = (
        select(Report)
        .options(joinedload(Report.city))
        .where(
            Report.city.has(City.name == city_name)
        )
    )

    return stmt


def _get_air_quality_data_rows(reports_results: List[Report]) -> List[AirQualityDataRow]:
    return [AirQualityDataRow.from_report(report) for report in reports_results]


async def get_air_quality_by_time_range(start_date: str, end_date: str) -> List[AirQualityDataRow]:
    if not utils.is_valid_date(start_date) or not utils.is_valid_date(end_date):
        raise NotValidDateException

    start_date = datetime.strptime(start_date, settings.DATE_FORMAT)
    end_date = datetime.strptime(end_date, settings.DATE_FORMAT)

    reports_results = await db.execute_with_scalar_results(_get_air_quality_time_range_stmt(start_date, end_date))
    data_rows = _get_air_quality_data_rows(reports_results)

    return data_rows


async def get_air_quality_by_city_name(city_name: str) -> List[AirQualityDataRow]:
    if not await city_service.is_existing_city(city_name):
        raise NotExistingCityException

    reports_results = await db.execute_with_scalar_results(_get_air_quality_city_stmt(city_name))
    data_rows = _get_air_quality_data_rows(reports_results)

    return data_rows
