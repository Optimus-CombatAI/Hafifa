
from fastapi import HTTPException
from starlette import status

from db.database import Database
from exceptions.notValidDateException import NotValidDateException
from exceptions.notExistingCityException import NotExistingCityException
from models.alertReturnRow import AlertReturnRow
from models.appRouter import AppRouter
from services.alerts_service import AlertsService


class AlertsRouter(AppRouter):
    def __init__(self, db: Database):
        super().__init__("/alerts", ["Alerts"], db, AlertsService)

        self.add_api_route("/", self.get_all_alerts_handler, methods=["GET"])
        self.add_api_route("/since", self.get_alerts_since_date_handler, methods=["GET"])
        self.add_api_route("/by_city", self.get_alerts_by_city_handler, methods=["GET"])

    async def get_all_alerts_handler(self) -> list[AlertReturnRow]:
        """
        This function returns all the recorded alerts
        :return: all the recorded alerts
        """
        return await self.service.get_all_alerts()

    async def get_alerts_since_date_handler(self, start_date: str) -> list[AlertReturnRow]:
        """
        This function returns all the recorded alerts that happened during the day
        :param start_date: the date of the day to get the alerts from
        :return: recorded alerts that happened during the day
        """

        try:
            alerts_since_start_date = await self.service.get_alerts_since_date(start_date)

            return alerts_since_start_date

        except NotValidDateException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    async def get_alerts_by_city_handler(self, city_name: str) -> list[AlertReturnRow]:
        """
        This function returns all the recorded alerts that happened in the city
        :param city_name: the name of the city to get the alerts from
        :return: recorded alerts that happened in the city
        """

        try:
            alerts_from_city = await self.service.get_alerts_by_city(city_name)

            return alerts_from_city

        except NotExistingCityException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
