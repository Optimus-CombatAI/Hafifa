from typing import Tuple

from fastapi import HTTPException, APIRouter
from starlette import status

from db.pgDatabase import PGDatabase
from exceptions.notExistingCityException import NotExistingCityException
from models.AQIDataRow import AQIDataRow
from services.aqi_statistics_service import AQIStatisticsService


class AQIStatisticsRouter(APIRouter):
    def __init__(self, db: PGDatabase):
        super().__init__(prefix="/aqi_statistics", tags=["AQI Statistics"])
        self.service = AQIStatisticsService(db)

        self.add_api_route("/history", self.get_aqi_history_by_city_handler, methods=["GET"])
        self.add_api_route("/average", self.get_avg_aqi_by_city_handler, methods=["GET"])
        self.add_api_route("/best_cities", self.get_aqi_best_cities_handler, methods=["GET"])

    async def get_aqi_history_by_city_handler(self, city_name: str) -> list[AQIDataRow]:
        """
        This function return the aqi history of a given city
        :param city_name: the name of the city to get history of aqi
        :return: aqi history of the given city
        """

        try:
            aqi_city_history = await self.service.get_aqi_history_by_city(city_name)

            return aqi_city_history

        except NotExistingCityException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

    async def get_avg_aqi_by_city_handler(self, city_name: str) -> Tuple[int, str]:
        """
        This function returns the average aqi score for a given city
        :param city_name: the name of the city to calculate the average aqi
        :return: the average aqi score
        """

        try:
            aqi_city_avg = await self.service.get_aqi_avg_by_city(city_name)

            return aqi_city_avg

        except NotExistingCityException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

    async def get_aqi_best_cities_handler(self) -> list[str]:
        """
        This function returns 3 cities with the best aqi score(the lowest score)
        :return: 3 cities with lowest aqi
        """

        return await self.service.get_3_best_cities()
