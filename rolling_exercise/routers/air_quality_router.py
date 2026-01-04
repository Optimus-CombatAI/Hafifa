
from fastapi import HTTPException, UploadFile, status, APIRouter
from starlette.responses import Response

from db.pgDatabase import PGDatabase
from models.airQualityDataRow import AirQualityDataRow
from exceptions.notValidDateException import NotValidDateException
from exceptions.notExistingCityException import NotExistingCityException
from exceptions.dbIntegrityException import DBIntegrityException
from services.air_quality_service import AirQualityService


class AirQualityRouter(APIRouter):
    def __init__(self, db: PGDatabase):
        super().__init__(prefix="/air_quality", tags=["Air Quality"])
        self.service = AirQualityService(db)

        self.add_api_route("/upload", self.upload_air_quality_handler, methods=["POST"])
        self.add_api_route("/by_time", self.get_air_quality_by_time_range_handler, methods=["GET"])
        self.add_api_route("/by_city", self.get_air_quality_by_city_handler, methods=["GET"])

    async def upload_air_quality_handler(self, file: UploadFile) -> Response:
        """
        This function adds to the database the weather data it receives and alerts if there are
        :param file: a multipart/form-data request containing a CSV file.
        :return: a response if created successfully
        """

        try:
            await self.service.upload_air_quality(file)

            return Response(status_code=status.HTTP_201_CREATED)

        except DBIntegrityException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    async def get_air_quality_by_time_range_handler(self, start_date: str, end_date: str) -> list[AirQualityDataRow]:
        """
        This function gets the weather data within a range for all the cities
        :param start_date: initial date of the range
        :param end_date: final date of the range
        :return: the weather within the range for all the cities
        """

        try:
            air_quality_data_rows = await self.service.get_air_quality_by_time_range(start_date, end_date)

            return air_quality_data_rows

        except NotValidDateException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    async def get_air_quality_by_city_handler(self, city_name: str) -> list[AirQualityDataRow]:
        """
        This function gets all the weather data for a given city
        :param city_name: the name of the city to get the weather from
        :return: all the weather in the city
        """

        try:
            air_quality_data_rows = await self.service.get_air_quality_by_city_name(city_name)

            return air_quality_data_rows

        except NotExistingCityException as e:
            raise HTTPException(status_code=404, detail=e.message)
