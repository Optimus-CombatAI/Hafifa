from datetime import datetime
from typing import List

from sqlalchemy import Select, select

from db.database import db
from entities.city import City
from entities.report import Report
from exceptions.notExistingCityException import NotExistingCityException
from exceptions.notValidDateException import NotValidDateException
from models.alertReturnRow import AlertReturnRow
from services import city_service
from settings import settings
from utils.utils import is_valid_date


def _get_all_alert_stmt() -> Select:
    stmt = (
        select(
            Report.id,
            Report.date,
            City.name,
            Report.overall_aqi,
            Report.aqi_level,
        )
        .join(Report.city)
        .where(
            Report.overall_aqi > 300
        )
    )

    return stmt


def _get_alert_return_rows(reports_results: List[Report]) -> List[AlertReturnRow]:
    return [AlertReturnRow.from_report(report) for report in reports_results]


async def get_all_alerts() -> List[AlertReturnRow]:

    stmt = _get_all_alert_stmt()
    alerts_results = await db.execute_with_plain_results(stmt)

    alerts_list = _get_alert_return_rows(alerts_results)

    return alerts_list


def _get_alerts_since_date_stmt(start_date: datetime) -> Select:
    stmt = (
        select(
            Report.id,
            Report.date,
            City.name,
            Report.overall_aqi,
            Report.aqi_level,
        )
        .join(Report.city)
        .where(
            (Report.overall_aqi > 300) & (Report.date > start_date)
        )
    )

    return stmt


async def get_alerts_since_date(start_date: str) -> List[AlertReturnRow]:

    if not is_valid_date(start_date):
        raise NotValidDateException

    start_date = datetime.strptime(start_date, settings.DATE_FORMAT)

    stmt = _get_alerts_since_date_stmt(start_date)
    alerts_results = await db.execute_with_plain_results(stmt)

    alerts_list = _get_alert_return_rows(alerts_results)

    return alerts_list


def _get_alerts_by_city_stmt(city_name: str) -> Select:
    stmt = (
        select(
            Report.id,
            Report.date,
            City.name,
            Report.overall_aqi,
            Report.aqi_level,
        )
        .join(Report.city)
        .where(
            (Report.overall_aqi > 300) & Report.city.has(City.name == city_name)
        )
    )

    return stmt


async def get_alerts_by_city(city_name) -> List[AlertReturnRow]:

    if not await city_service.is_existing_city(city_name):
        raise NotExistingCityException

    stmt = _get_alerts_by_city_stmt(city_name)
    alerts_results = await db.execute_with_plain_results(stmt)

    alerts_list = _get_alert_return_rows(alerts_results)

    return alerts_list
