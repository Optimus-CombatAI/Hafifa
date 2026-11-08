from datetime import date

import pytest

from src.models.alert_response import AlertResponse
from src.repositories.air_quality_repository import AirQualityRepository
from src.repositories.alert_repository import AlertRepository
from src.services.alert_query_service import AlertQueryService
from tests.records import make_record


@pytest.fixture
def air_quality_repository(session) -> AirQualityRepository:
    return AirQualityRepository(session)


@pytest.fixture
def service(session) -> AlertQueryService:
    return AlertQueryService(AlertRepository(session))


def test_alerts_are_returned_as_responses(service, air_quality_repository):
    air_quality_repository.save_all([make_record(date=date(2024, 11, 19), city="Haifa", aqi=350, with_alert=True)])

    alerts = service.get_all()

    assert alerts == [AlertResponse(date=date(2024, 11, 19), city="Haifa", aqi=350)]


def test_city_with_data_but_no_alerts_gets_empty_list(service, air_quality_repository):
    air_quality_repository.save_all([make_record(city="Eilat", aqi=30)])

    alerts = service.get_by_city("Eilat")

    assert alerts == []
