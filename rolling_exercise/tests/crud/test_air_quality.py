import pytest
import datetime
import fastapi

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from unittest.mock import Mock

from rolling_exercise.crud.air_quality import (
    get_air_quality_by_date_range,
    get_air_quality_by_city,
    get_city_aqi_history,
    get_city_aqi_average,
    get_best_cities,
)
from rolling_exercise.models.air_quality import AirQuality


def get_mock_db_session():
    return Mock(spec=Session)


def test_get_air_quality_by_date_range():
    mock_db = get_mock_db_session()
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 1, 31)

    mock_records = [
        AirQuality(date=start_date, city='TestCity', aqi=50),
        AirQuality(date=end_date, city='TestCity', aqi=60)
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_records

    result = get_air_quality_by_date_range(start_date, end_date, mock_db)

    assert len(result) == 2
    assert all(record.city == 'TestCity' for record in result)


def test_get_air_quality_by_date_range_no_records():
    mock_db = get_mock_db_session()
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 1, 31)

    mock_db.query.return_value.filter.return_value.all.return_value = []

    with pytest.raises(fastapi.HTTPException) as error:
        get_air_quality_by_date_range(start_date, end_date, mock_db)

    assert error.value.status_code == 404
    assert "No air quality data found" in str(error.value.detail["message"])


def test_get_air_quality_by_date_range_invalid_date_format():
    mock_db = get_mock_db_session()
    start_date = "2023-01-01"
    end_date = "2023-01-31"

    with pytest.raises(fastapi.HTTPException) as error:
        get_air_quality_by_date_range(start_date, end_date, mock_db)

    assert error.value.status_code == 422
    assert "Invalid date format" in str(error.value.detail["message"])


def test_get_air_quality_by_date_range_invalid_date_order():
    mock_db = get_mock_db_session()
    start_date = datetime.date(2023, 2, 1)
    end_date = datetime.date(2023, 1, 31)

    with pytest.raises(fastapi.HTTPException) as error:
        get_air_quality_by_date_range(start_date, end_date, mock_db)

    assert error.value.status_code == 422
    assert "Start date cannot be after end date" in str(error.value.detail["message"])


def test_get_air_quality_by_city():
    mock_db = get_mock_db_session()
    city = 'TestCity'

    mock_records = [
        AirQuality(city=city, date=datetime.date(2023, 1, 1), aqi=50),
        AirQuality(city=city, date=datetime.date(2023, 1, 2), aqi=60)
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_records

    result = get_air_quality_by_city(city, mock_db)

    assert len(result) == 2
    assert all(record.city == city for record in result)


def test_get_air_quality_by_city_no_records():
    mock_db = get_mock_db_session()
    city = 'NonExistentCity'

    mock_db.query.return_value.filter.return_value.all.return_value = []

    with pytest.raises(fastapi.HTTPException) as exc_info:
        get_air_quality_by_city(city, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail["message"] == f"No air quality data found for city {city}."


def test_get_city_aqi_history():
    mock_db = get_mock_db_session()
    city = 'TestCity'

    mock_records = [
        Mock(date=datetime.date(2023, 1, 1), aqi=50, aqi_level='Moderate'),
        Mock(date=datetime.date(2023, 1, 2), aqi=60, aqi_level='Unhealthy')
    ]
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_records

    result = get_city_aqi_history(city, mock_db)

    assert 'data' in result
    assert result['data']['city'] == city
    assert len(result['data']['history']) == 2


def test_get_city_aqi_history_no_records():
    mock_db = get_mock_db_session()
    city = 'NonExistentCity'

    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

    with pytest.raises(fastapi.HTTPException) as exc_info:
        get_city_aqi_history(city, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail["message"] == f"No AQI history found for city {city}."


def test_get_city_aqi_average():
    mock_db = get_mock_db_session()
    city = 'TestCity'

    mock_avg = [(55.5,)]
    mock_db.query.return_value.filter.return_value.one.return_value = mock_avg

    result = get_city_aqi_average(city, mock_db)

    assert 'data' in result
    assert result['data']['city'] == city
    assert result['data']['average_aqi'] == 55.5


def test_get_city_aqi_average_no_records():
    mock_db = get_mock_db_session()
    city = 'NonExistentCity'

    mock_db.query.return_value.filter.return_value.one.side_effect = NoResultFound

    with pytest.raises(fastapi.HTTPException) as exc_info:
        get_city_aqi_average(city, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail["message"] == f"No AQI data found for city {city}."


def test_get_best_cities():
    mock_db = get_mock_db_session()

    mock_cities = [
        Mock(city='City1', average_aqi=40),
        Mock(city='City2', average_aqi=50),
        Mock(city='City3', average_aqi=60)
    ]
    mock_db.query.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = mock_cities

    result = get_best_cities(mock_db)

    assert 'data' in result
    assert len(result['data']['best_cities']) == 3


def test_get_best_cities_no_records():
    mock_db = get_mock_db_session()

    mock_db.query.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = []

    with pytest.raises(fastapi.HTTPException) as exc_info:
        get_best_cities(mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail["message"] == "No cities found with AQI data."
