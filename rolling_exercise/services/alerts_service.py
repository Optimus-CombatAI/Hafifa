from datetime import datetime
from typing import List

from sqlalchemy import Select, select

from db.pgDatabase import PGDatabase
from entities.city import City
from entities.report import Report
from exceptions.notExistingCityException import NotExistingCityException
from exceptions.notValidDateException import NotValidDateException
from models.alertReturnRow import AlertReturnRow
from services.service import Service
from services.city_service import CityService
from settings import settings
from utils.serviceUtils import is_valid_date


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
            Report.overall_aqi > settings.ALERT_OVERALL_AQI
        )
    )

    return stmt


def _get_alert_return_rows(reports_results: List[Report]) -> List[AlertReturnRow]:
    return [AlertReturnRow.from_report(report) for report in reports_results]


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
            (Report.overall_aqi > settings.ALERT_OVERALL_AQI) & (Report.date > start_date)
        )
    )

    return stmt


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
            (Report.overall_aqi > settings.ALERT_OVERALL_AQI) & Report.city.has(City.name == city_name)
        )
    )

    return stmt


class AlertsService(Service):
    def __init__(self, db: PGDatabase):
        super().__init__(db)
        self.city_service = CityService(db)

    async def get_all_alerts(self) -> List[AlertReturnRow]:
    
        stmt = _get_all_alert_stmt()
        alerts_results = await self.db.execute_with_plain_results(stmt)
    
        alerts_list = _get_alert_return_rows(alerts_results)
    
        return alerts_list
    
    async def get_alerts_since_date(self, start_date: str) -> List[AlertReturnRow]:

        if not is_valid_date(start_date):
            raise NotValidDateException

        start_date = datetime.strptime(start_date, settings.DATE_FORMAT)

        stmt = _get_alerts_since_date_stmt(start_date)
        alerts_results = await self.db.execute_with_plain_results(stmt)

        alerts_list = _get_alert_return_rows(alerts_results)

        return alerts_list

    async def get_alerts_by_city(self, city_name) -> List[AlertReturnRow]:
    
        if not await self.city_service.is_existing_city(city_name):
            raise NotExistingCityException
    
        stmt = _get_alerts_by_city_stmt(city_name)
        alerts_results = await self.db.execute_with_plain_results(stmt)
    
        alerts_list = _get_alert_return_rows(alerts_results)
    
        return alerts_list
