from datetime import date

import pytest

from src.errors import CityNotFoundError
from src.models.aqi_history_entry import AqiHistoryEntry
from src.models.city_average_aqi import CityAverageAqi
from src.models.date_range_query import DateRangeQuery
from src.repositories.air_quality_repository import AirQualityRepository
from src.services.air_quality_query_service import AirQualityQueryService
from tests.records import make_record


@pytest.fixture
def repository(session) -> AirQualityRepository:
    return AirQualityRepository(session)


@pytest.fixture
def service(repository) -> AirQualityQueryService:
    return AirQualityQueryService(repository)


def test_get_by_date_range_returns_records_in_range(service, repository):
    repository.save_all(
        [
            make_record(date=date(2024, 11, 19), city="Haifa", aqi=100),
            make_record(date=date(2024, 11, 20), city="Haifa", aqi=200),
        ]
    )

    responses = service.get_by_date_range(DateRangeQuery(start_date=date(2024, 11, 19), end_date=date(2024, 11, 19)))

    (response,) = responses
    assert response.city == "Haifa"
    assert response.aqi == 100


def test_get_by_city_returns_every_record_of_the_city(service, repository):
    repository.save_all(
        [
            make_record(date=date(2024, 11, 19), city="Haifa"),
            make_record(date=date(2024, 11, 20), city="Haifa"),
            make_record(date=date(2024, 11, 19), city="Akko"),
        ]
    )

    responses = service.get_by_city("Haifa")

    assert [response.date for response in responses] == [date(2024, 11, 19), date(2024, 11, 20)]


def test_get_aqi_history_returns_date_and_aqi_of_each_day(service, repository):
    repository.save_all(
        [
            make_record(date=date(2024, 11, 19), city="Haifa", aqi=40, aqi_level="Good"),
            make_record(date=date(2024, 11, 20), city="Haifa", aqi=180, aqi_level="Unhealthy"),
        ]
    )

    history = service.get_aqi_history("Haifa")

    assert history == [
        AqiHistoryEntry(date=date(2024, 11, 19), aqi=40, aqi_level="Good"),
        AqiHistoryEntry(date=date(2024, 11, 20), aqi=180, aqi_level="Unhealthy"),
    ]


def test_get_aqi_average_returns_the_city_and_its_average(service, repository):
    repository.save_all(
        [
            make_record(date=date(2024, 11, 19), city="Haifa", aqi=100),
            make_record(date=date(2024, 11, 20), city="Haifa", aqi=200),
        ]
    )

    average = service.get_aqi_average("Haifa")

    assert average == CityAverageAqi(city="Haifa", average_aqi=150)


def test_get_best_cities_returns_requested_count(service, repository):
    repository.save_all([make_record(city="Haifa"), make_record(city="Akko"), make_record(city="Eilat")])

    best_cities = service.get_best_cities(2)

    assert len(best_cities) == 2


@pytest.mark.parametrize(
    "get_city_data",
    [
        AirQualityQueryService.get_by_city,
        AirQualityQueryService.get_aqi_history,
        AirQualityQueryService.get_aqi_average,
    ],
)
def test_city_without_data_raises_not_found(service, repository, get_city_data):
    repository.save_all([make_record(city="Haifa")])

    with pytest.raises(CityNotFoundError, match="Atlantis"):
        get_city_data(service, "Atlantis")
