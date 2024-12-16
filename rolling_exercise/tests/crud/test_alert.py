import pytest
import datetime as dt
import fastapi
import sqlalchemy
from unittest.mock import Mock

from rolling_exercise.models.alert import Alert
from rolling_exercise.crud.alert import (
    get_all_alerts,
    get_alerts_by_date,
    get_alerts_by_city,
)


def get_mock_db_session():
    return Mock(spec=sqlalchemy.orm.Session)


def test_get_all_alerts():
    mock_db = get_mock_db_session()

    mock_alerts = [
        Alert(date=dt.date(2023, 1, 1), city='TestCity', aqi=50.5, aqi_level='Good'),
        Alert(date=dt.date(2023, 1, 2), city='TestCity', aqi=60.0, aqi_level='Moderate')
    ]
    mock_db.query.return_value.all.return_value = mock_alerts

    result = get_all_alerts(mock_db)

    assert len(result) == 2
    assert all(alert.city == 'TestCity' for alert in result)


def test_get_all_alerts_no_records():
    mock_db = get_mock_db_session()

    mock_db.query.return_value.all.return_value = []

    with pytest.raises(fastapi.HTTPException) as error:
        get_all_alerts(mock_db)

    assert error.value.status_code == 404
    assert "No alerts found" in str(error.value.detail["message"])


def test_get_alerts_by_date():
    mock_db = get_mock_db_session()
    test_date = dt.date(2023, 1, 1)

    mock_alerts = [
        Alert(date=test_date, city='TestCity', aqi=50.5, aqi_level='Good'),
        Alert(date=test_date, city='TestCity', aqi=55.0, aqi_level='Moderate')
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_alerts

    result = get_alerts_by_date(test_date, mock_db)

    assert len(result) == 2
    assert all(alert.date == test_date for alert in result)


def test_get_alerts_by_date_no_records():
    mock_db = get_mock_db_session()
    test_date = dt.date(2023, 1, 1)

    mock_db.query.return_value.filter.return_value.all.return_value = []

    with pytest.raises(fastapi.HTTPException) as error:
        get_alerts_by_date(test_date, mock_db)

    assert error.value.status_code == 404
    assert f"No alerts found for date {test_date}" in str(error.value.detail["message"])


def test_get_alerts_by_city():
    mock_db = get_mock_db_session()
    test_city = 'TestCity'

    mock_alerts = [
        Alert(date=dt.date(2023, 1, 1), city=test_city, aqi=50.5, aqi_level='Good'),
        Alert(date=dt.date(2023, 1, 2), city=test_city, aqi=60.0, aqi_level='Moderate')
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_alerts

    result = get_alerts_by_city(test_city, mock_db)

    assert len(result) == 2
    assert all(alert.city == test_city for alert in result)


def test_get_alerts_by_city_no_records():
    mock_db = get_mock_db_session()
    test_city = 'TestCity'

    mock_db.query.return_value.filter.return_value.all.return_value = []

    with pytest.raises(fastapi.HTTPException) as error:
        get_alerts_by_city(test_city, mock_db)

    assert error.value.status_code == 404
    assert f"No alerts found for city {test_city}" in str(error.value.detail["message"])
