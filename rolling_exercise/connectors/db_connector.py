
from datetime import datetime, timedelta
from typing import Dict, List
import re
import random

import logging
import pandas as pd
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from db.database import db
from db.cities_table import cities
from db.reports_table import reports
from entities.city import City
from entities.report import Report
from exceptions.duplicateDataException import DuplicateDataException
from models.AQIDataRow import AQIDataRow
from models.airQualityDataRow import AirQualityDataRow
from models.alertReturnRow import AlertReturnRow
from utils.utils import get_aqi_level
from settings import settings


logger = logging.getLogger(__name__)


async def is_existing_city(city_name) -> bool:
    stmt = (
        select(Report)
        .options(joinedload(Report.city))
        .where(
            Report.city.has(City.name == city_name)
        )
    )
    
    async with db.session() as session:
        result = await session.scalars(stmt)
        reports_results = result.all()

    return len(reports_results) != 0


async def insert_cities(city_names_df: pd.DataFrame) -> None:
    city_names_df = city_names_df.rename(columns={"city": "name"})

    stmt = insert(City).values(city_names_df.to_dict(orient="records"))
    stmt = stmt.on_conflict_do_nothing(index_elements=["name"])

    async with db.session() as session:
        await session.execute(stmt)


async def _get_cities_to_id_map() -> Dict[str, str]:
    async with db.session() as session:
        result = await session.execute(select(City.id, City.name))
        existing_cities = result.mappings().all()
        existing_map = {row["name"]: row["id"] for row in existing_cities}
        return existing_map


async def _get_reports_statements(reports_df: pd.DataFrame) -> List[Report]:
    city_name_to_id_map = await _get_cities_to_id_map()
    reports_to_insert = []

    for _, row in reports_df.iterrows():
        city_id = city_name_to_id_map.get(row["name"])

        reports_to_insert.append(
            Report(
                city_id=city_id,
                date=pd.to_datetime(row["date"]).date(),
                pm2_5=int(row["PM2.5"]),
                no2=int(row["NO2"]),
                co2=int(row["CO2"]),
                overall_aqi=int(row["overall_aqi"]),
                aqi_level=row["aqi_level"]
            )
        )

    return reports_to_insert


async def _extract_city_name_and_date(error_message: str) -> tuple[str, datetime.date]:

    pattern = r"\((\d{4}-\d{2}-\d{2}),\s*(\d+)\)"
    match = re.search(pattern, error_message)

    if match:
        date = datetime.strptime(match.group(1), '%Y-%m-%d').date()
        city_id = int(match.group(2))

        name_to_id_map = await _get_cities_to_id_map()
        city_name = next((k for k, v in name_to_id_map.items() if v == city_id), None)

        return city_name, date


async def _handle_duplication_error(exception: IntegrityError):
    pg_code = getattr(exception.orig, 'pgcode', None)

    if pg_code == settings.DUPLICATION_ERROR:
        detail_msg = exception.orig.args[0]
        city_name, date = await _extract_city_name_and_date(detail_msg)

        raise DuplicateDataException(city_name, date)


async def insert_reports(reports_df: pd.DataFrame) -> None:

    logger.info(reports_df)

    reports_to_insert = await _get_reports_statements(reports_df)

    try:
        async with db.session() as session:
            session.add_all(reports_to_insert)

    except IntegrityError as e:
        await _handle_duplication_error(e)


def _get_air_quality_data_rows(reports_results: List[Report]) -> List[AirQualityDataRow]:
    return [AirQualityDataRow(
        city_name=report.city.name,
        report_date=report.date,
        pm2_5_value=report.pm2_5,
        no2_value=report.no2,
        co2_value=report.co2,
        overall_aqi=report.overall_aqi,
        aqi_level=report.aqi_level
    ) for report in reports_results]


async def get_air_quality_by_time_range(start_date: datetime.date, end_date: datetime.date) -> list[AirQualityDataRow]:
    stmt = (
        select(Report)
        .options(joinedload(Report.city))
        .where(
            Report.date.between(start_date, end_date)
        )
    )

    async with db.session() as session:
        result = await session.scalars(stmt)
        reports_results = result.all()
        
    data_rows = _get_air_quality_data_rows(reports_results)

    return data_rows


async def get_air_quality_by_city_name(city_name: str) -> list[AirQualityDataRow]:
    stmt = (
        select(Report)
        .options(joinedload(Report.city))
        .where(
            Report.city.has(City.name == city_name)
        )
    )

    async with db.session() as session:
        result = await session.scalars(stmt)
        reports_results = result.all()
    
    data_rows = _get_air_quality_data_rows(reports_results)

    return data_rows


async def get_aqi_history_by_city(city_name: str) -> List[AQIDataRow]:
    stmt = (
        select(Report)
        .options(joinedload(Report.city))
        .where(
            Report.city.has(City.name == city_name)
        )
    )

    async with db.session() as session:
        result = await session.scalars(stmt)
        reports_results = result.all()

    data_rows = [AQIDataRow(
            overall_aqi=report.overall_aqi,
            aqi_level=report.aqi_level
        ) for report in reports_results]

    return data_rows


async def get_aqi_avg_by_city(city_name: str) -> AQIDataRow:
    stmt = (
        select(
            func.avg(Report.overall_aqi),
        )
        .where(
            Report.city.has(City.name == city_name)
        )
    )

    async with db.session() as session:
        result = await session.scalars(stmt)
        reports_results = result.all()

    overall_aqi = int(reports_results[0])

    data_row = AQIDataRow(
            overall_aqi=overall_aqi,
            aqi_level=get_aqi_level(overall_aqi)
        )

    return data_row


async def get_3_best_cities() -> list[str]:
    stmt = (
        select(
            City.name,
            func.min(Report.overall_aqi)
        )
        .join(Report)
        .group_by(City.id)
        .order_by(func.min(Report.overall_aqi).asc())
        .limit(3)
    )

    async with db.session() as session:
        result = await session.scalars(stmt)
        reports_results = result.all()

    city_names = [city_name for city_name in reports_results]

    return city_names


def _get_alert_return_rows(reports_results: List[Report]) -> List[AlertReturnRow]:
    return [AlertReturnRow(
        id=report.id,
        city_name=report.city.name,
        date=report.date,
        overall_aqi=report.overall_aqi,
        aqi_level=report.aqi_level
    ) for report in reports_results]


async def get_all_alerts() -> list[AlertReturnRow]:
    stmt = (
        select(
            Report,
        )
        .options(selectinload(Report.city))
        .where(
            Report.overall_aqi > 300
        )
    )

    async with db.session() as session:
        result = await session.scalars(stmt)
        reports_results = result.all()

    alerts_list = _get_alert_return_rows(reports_results)

    return alerts_list


async def get_alerts_since_date(start_date: datetime.date) -> list[AlertReturnRow]:
    stmt = (
        select(
            Report,
        )
        .options(selectinload(Report.city))
        .where(
            (Report.overall_aqi > 300) & (Report.date > start_date)
        )
    )

    async with db.session() as session:
        result = await session.scalars(stmt)
        reports_results = result.all()

    alerts_list = _get_alert_return_rows(reports_results)

    return alerts_list


async def get_alerts_by_city(city_name: str) -> list[AlertReturnRow]:
    stmt = (
        select(
            Report,
        )
        .options(joinedload(Report.city))
        .where(
            (Report.overall_aqi > 300) & Report.city.has(City.name == city_name)
        )
    )

    async with db.session() as session:
        result = await session.scalars(stmt)
        reports_results = result.all()

    alerts_list = _get_alert_return_rows(reports_results)

    return alerts_list


def _get_random_date(start: datetime = datetime(2025, 11, 10),
                     end: datetime = datetime(2025, 11, 15)) -> datetime.date:
    delta = end - start
    random_days = random.randint(0, delta.days)

    return (start + timedelta(days=random_days)).date()


async def fill_dummy_data(use_dummy_dataset=False) -> None:
    if use_dummy_dataset:
        random_cities = ['Be\'er Sheva', 'Holon', 'Haifa', 'Tel Aviv', 'Netanya']
        levels = ["Good", "Moderate", "Unhealthy for Sensitive Groups", "Unhealthy", "Very Unhealthy", "Hazardous"]
        city_stmt = [insert(cities).values(name=city_name) for city_name in random_cities]
        report_stmt = []

        for i in range(5):
            report_stmt.append(
                insert(reports).values(date=_get_random_date(), city_id=random.randint(1, len(random_cities)),
                                       pm2_5=random.randint(1, 10), no2=random.randint(1, 10),
                                       co2=random.randint(1, 10),
                                       overall_aqi=random.randint(1, 10), aqi_level=random.choice(levels))
            )

        async with db.engine.begin() as conn:
            for stmt in city_stmt:
                await conn.execute(stmt)
            for stmt in report_stmt:
                await conn.execute(stmt)

            logger.info("Inserted successfully with Core.")
