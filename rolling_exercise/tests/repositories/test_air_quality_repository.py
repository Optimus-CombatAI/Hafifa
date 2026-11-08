from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from src.models.city_average_aqi import CityAverageAqi
from src.repositories.air_quality_repository import AirQualityRepository
from tests.records import make_record


@pytest.fixture
def repository(session) -> AirQualityRepository:
    return AirQualityRepository(session)


def test_get_cities_by_dates_returns_only_those_dates(repository):
    repository.save_all(
        [
            make_record(date=date(2024, 11, 19), city="Haifa"),
            make_record(date=date(2024, 11, 20), city="Akko"),
            make_record(date=date(2024, 11, 21), city="Eilat"),
        ]
    )

    city_days = repository.get_cities_by_dates({date(2024, 11, 19), date(2024, 11, 21)})

    assert city_days == {(date(2024, 11, 19), "Haifa"), (date(2024, 11, 21), "Eilat")}


def test_get_by_date_range_includes_both_ends(repository):
    repository.save_all(
        [
            make_record(date=date(2024, 11, 18)),
            make_record(date=date(2024, 11, 19)),
            make_record(date=date(2024, 11, 20)),
            make_record(date=date(2024, 11, 21)),
        ]
    )

    records = repository.get_by_date_range(date(2024, 11, 19), date(2024, 11, 20))

    assert [record.date for record in records] == [date(2024, 11, 19), date(2024, 11, 20)]


def test_get_by_date_range_is_ordered_by_date_then_city(repository):
    repository.save_all(
        [
            make_record(date=date(2024, 11, 20), city="Haifa"),
            make_record(date=date(2024, 11, 20), city="Akko"),
            make_record(date=date(2024, 11, 19), city="Eilat"),
        ]
    )

    records = repository.get_by_date_range(date(2024, 11, 19), date(2024, 11, 20))

    assert [record.city for record in records] == ["Eilat", "Akko", "Haifa"]


def test_get_by_city_ignores_case(repository):
    repository.save_all([make_record(city="Haifa"), make_record(city="Akko")])

    records = repository.get_by_city("haifa")

    assert [record.city for record in records] == ["Haifa"]


def test_get_city_aqi_average_counts_only_that_city(repository):
    repository.save_all(
        [
            make_record(date=date(2024, 11, 19), city="Haifa", aqi=100),
            make_record(date=date(2024, 11, 20), city="Haifa", aqi=200),
            make_record(date=date(2024, 11, 19), city="Akko", aqi=400),
        ]
    )

    average = repository.get_city_aqi_average("Haifa")

    assert average == 150


def test_get_city_aqi_average_of_unknown_city_is_none(repository):
    average = repository.get_city_aqi_average("Atlantis")

    assert average is None


def test_get_best_cities_returns_lowest_averages_first(repository):
    repository.save_all(
        [
            make_record(date=date(2024, 11, 19), city="Haifa", aqi=100),
            make_record(date=date(2024, 11, 20), city="Haifa", aqi=200),
            make_record(date=date(2024, 11, 19), city="Netanya", aqi=50),
            make_record(date=date(2024, 11, 20), city="Netanya", aqi=70),
            make_record(date=date(2024, 11, 19), city="Eilat", aqi=30),
            make_record(date=date(2024, 11, 19), city="Akko", aqi=400),
        ]
    )

    best_cities = repository.get_best_cities(limit=3)

    assert best_cities == [
        CityAverageAqi(city="Eilat", average_aqi=30),
        CityAverageAqi(city="Netanya", average_aqi=60),
        CityAverageAqi(city="Haifa", average_aqi=150),
    ]


def test_same_city_and_date_twice_is_refused(repository):
    repository.save_all([make_record(date=date(2024, 11, 19), city="Haifa")])

    with pytest.raises(IntegrityError):
        repository.save_all([make_record(date=date(2024, 11, 19), city="Haifa")])
