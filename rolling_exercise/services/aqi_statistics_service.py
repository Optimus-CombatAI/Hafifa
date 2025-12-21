from typing import List

from sqlalchemy import select, func, Select

from exceptions.notExistingCityException import NotExistingCityException
from entities.city import City
from entities.report import Report
from models.AQIDataRow import AQIDataRow
import services.city_service as city_service
from db.database import db
from utils.utils import get_aqi_level


def _get_aqi_history_by_city_stmt(city_name: str) -> Select:
    stmt = (
        select(
            Report.overall_aqi,
            Report.aqi_level
        )
        .where(
            Report.city.has(City.name == city_name)
        )
    )

    return stmt


def _construct_history_aqi_data_row(reports_results: List[Report]) -> List[AQIDataRow]:
    data_rows = [AQIDataRow.from_results((
        report.overall_aqi, report.aqi_level
    )) for report in reports_results]

    return data_rows


async def get_aqi_history_by_city(city_name: str) -> List[AQIDataRow]:
    if not await city_service.is_existing_city(city_name):
        raise NotExistingCityException

    stmt = _get_aqi_history_by_city_stmt(city_name)
    reports_results = await db.execute_with_plain_results(stmt)

    aqi_data_rows = _construct_history_aqi_data_row(reports_results)

    return aqi_data_rows


def _construct_avg_data_row(overall_aqi: str) -> AQIDataRow:
    overall_aqi = int(overall_aqi)

    aqi_data_row = AQIDataRow.from_results((
        overall_aqi, get_aqi_level(overall_aqi)
    ))

    return aqi_data_row


def _get_aqi_avg_by_city_stmt(city_name: str) -> Select:
    stmt = (
        select(
            func.avg(Report.overall_aqi),
        )
        .where(
            Report.city.has(City.name == city_name)
        )
    )

    return stmt


async def get_aqi_avg_by_city(city_name: str) -> AQIDataRow:
    if not await city_service.is_existing_city(city_name):
        raise NotExistingCityException

    stmt = _get_aqi_avg_by_city_stmt(city_name)
    result = await db.execute_with_scalar_results(stmt)

    aqi_data_row = _construct_avg_data_row(result[0])

    return aqi_data_row


def _get_best_city_stmt():
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

    return stmt


async def get_3_best_cities() -> List[str]:
    stmt = _get_best_city_stmt()

    city_names = await db.execute_with_scalar_results(stmt)

    return city_names
