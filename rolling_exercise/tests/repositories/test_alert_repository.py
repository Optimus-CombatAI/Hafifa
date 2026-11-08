from datetime import date

import pytest

from src.repositories.air_quality_repository import AirQualityRepository
from src.repositories.alert_repository import AlertRepository
from tests.records import make_record


@pytest.fixture
def air_quality_repository(session) -> AirQualityRepository:
    return AirQualityRepository(session)


@pytest.fixture
def repository(session) -> AlertRepository:
    return AlertRepository(session)


def test_alert_is_saved_with_its_record(repository, air_quality_repository):
    air_quality_repository.save_all([make_record(city="Haifa", aqi=350, with_alert=True)])

    (alert,) = repository.get_all()
    assert alert.city == "Haifa"
    assert alert.aqi == 350
    assert alert.air_quality_record.city == "Haifa"


def test_get_all_is_ordered_by_date_then_city(repository, air_quality_repository):
    air_quality_repository.save_all(
        [
            make_record(date=date(2024, 11, 20), city="Haifa", with_alert=True),
            make_record(date=date(2024, 11, 20), city="Akko", with_alert=True),
            make_record(date=date(2024, 11, 19), city="Eilat", with_alert=True),
        ]
    )

    alerts = repository.get_all()

    assert [alert.city for alert in alerts] == ["Eilat", "Akko", "Haifa"]


def test_get_by_date_returns_only_that_date(repository, air_quality_repository):
    air_quality_repository.save_all(
        [
            make_record(date=date(2024, 11, 19), city="Haifa", with_alert=True),
            make_record(date=date(2024, 11, 20), city="Akko", with_alert=True),
        ]
    )

    alerts = repository.get_by_date(date(2024, 11, 20))

    assert [alert.city for alert in alerts] == ["Akko"]


def test_get_by_city_ignores_case(repository, air_quality_repository):
    air_quality_repository.save_all(
        [
            make_record(city="Haifa", with_alert=True),
            make_record(city="Akko", with_alert=True),
        ]
    )

    alerts = repository.get_by_city("HAIFA")

    assert [alert.city for alert in alerts] == ["Haifa"]
