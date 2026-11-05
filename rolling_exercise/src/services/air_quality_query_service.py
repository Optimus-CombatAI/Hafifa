from src.db.air_quality_record import AirQualityRecord
from src.errors import CityNotFoundError
from src.models.air_quality_response import AirQualityResponse
from src.models.aqi_history_entry import AqiHistoryEntry
from src.models.city_average_aqi import CityAverageAqi
from src.models.date_range_query import DateRangeQuery
from src.repositories.air_quality_repository import AirQualityRepository


class AirQualityQueryService:
    def __init__(self, air_quality_repository: AirQualityRepository):
        self._air_quality_repository = air_quality_repository

    def get_by_date_range(self, date_range: DateRangeQuery) -> list[AirQualityResponse]:
        records = self._air_quality_repository.get_by_date_range(date_range.start_date, date_range.end_date)

        return [AirQualityResponse.model_validate(record) for record in records]

    def get_by_city(self, city: str) -> list[AirQualityResponse]:
        return [AirQualityResponse.model_validate(record) for record in self._get_city_records(city)]

    def get_aqi_history(self, city: str) -> list[AqiHistoryEntry]:
        return [AqiHistoryEntry.model_validate(record) for record in self._get_city_records(city)]

    def get_aqi_average(self, city: str) -> CityAverageAqi:
        average_aqi = self._air_quality_repository.get_city_aqi_average(city)

        if average_aqi is None:
            raise CityNotFoundError(city)

        return CityAverageAqi(city=city, average_aqi=average_aqi)

    def get_best_cities(self, count: int) -> list[CityAverageAqi]:
        return self._air_quality_repository.get_best_cities(count)

    def _get_city_records(self, city: str) -> list[AirQualityRecord]:
        records = self._air_quality_repository.get_by_city(city)

        if not records:
            raise CityNotFoundError(city)

        return records
