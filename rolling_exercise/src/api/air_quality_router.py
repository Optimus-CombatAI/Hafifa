from typing import Annotated

from fastapi import APIRouter, Query

from src.api.dependencies import AirQualityQueryServiceDependency
from src.models.air_quality_response import AirQualityResponse
from src.models.aqi_history_entry import AqiHistoryEntry
from src.models.city_average_aqi import CityAverageAqi
from src.models.date_range_query import DateRangeQuery

router = APIRouter(prefix="/air-quality", tags=["air quality"])


@router.get("")
def get_air_quality_by_date_range(
    date_range: Annotated[DateRangeQuery, Query()], query_service: AirQualityQueryServiceDependency
) -> list[AirQualityResponse]:
    return query_service.get_by_date_range(date_range)


@router.get("/by-city")
def get_air_quality_by_city(city: str, query_service: AirQualityQueryServiceDependency) -> list[AirQualityResponse]:
    return query_service.get_by_city(city)


@router.get("/aqi-history")
def get_city_aqi_history(city: str, query_service: AirQualityQueryServiceDependency) -> list[AqiHistoryEntry]:
    return query_service.get_aqi_history(city)


@router.get("/aqi-average")
def get_city_aqi_average(city: str, query_service: AirQualityQueryServiceDependency) -> CityAverageAqi:
    return query_service.get_aqi_average(city)


@router.get("/best-cities")
def get_best_cities(
    query_service: AirQualityQueryServiceDependency, count: Annotated[int, Query(ge=1)] = 3
) -> list[CityAverageAqi]:
    return query_service.get_best_cities(count)
