import pytest
import pandas as pd
import datetime
from unittest.mock import Mock
import fastapi

from rolling_exercise.utils.upload import (
    read_csv_file,
    validate_records,
    process_csv,
    create_db_records,
    save_records_to_db,
)
from rolling_exercise.models.air_quality import AirQuality
from rolling_exercise.models.alert import Alert
from rolling_exercise.schemas.air_quality import AirQualityBase


def test_read_csv_file():
    test_csv_content = b"date,city,PM2.5,NO2,CO2\n2023-01-01,TestCity,10,20,30"
    filename = "test.csv"

    result = read_csv_file(test_csv_content, filename)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result['city'].iloc[0] == 'TestCity'


def test_read_csv_file_parsing_error():
    test_csv_content = b"col1,col2\nval1"
    filename = "test.csv"

    with pytest.raises(fastapi.HTTPException) as error:
        read_csv_file(test_csv_content, filename)

    assert "could not be parsed" in str(error.value.detail["message"])


@pytest.mark.asyncio
async def test_process_csv():
    csv_content = b"date,city,PM2.5,NO2,CO2\n2023-01-01,TestCity,10,20,30"
    mock_upload_file = Mock()
    mock_upload_file.filename = "test.csv"
    mock_upload_file.read = Mock(return_value=csv_content)

    records, validation_errors = await process_csv(mock_upload_file)

    assert len(records) == 1
    assert len(validation_errors) == 0


@pytest.mark.asyncio
async def test_process_csv_no_valid_data():
    csv_content = b"date,city,PM2.5,NO2,CO2\n2023-01-01,TestCity,invalid,invalid,invalid"
    mock_upload_file = Mock()
    mock_upload_file.filename = "test.csv"
    mock_upload_file.read = Mock(return_value=csv_content)

    with pytest.raises(fastapi.HTTPException) as error:
        await process_csv(mock_upload_file)

    assert "No valid data found" in str(error.value.detail["message"])


def test_validate_records():
    df = pd.DataFrame({
        'date': ['2023-01-01'],
        'city': ['TestCity'],
        'PM2.5': [10],
        'NO2': [20],
        'CO2': [30]
    })
    filename = "test.csv"

    records, validation_errors = validate_records(df, filename)

    assert len(records) == 1
    assert len(validation_errors) == 0


def test_validate_records_with_invalid_data():
    df = pd.DataFrame({
        'date': ['invalid_date'],
        'city': [None],
        'PM2.5': ['not_a_number'],
        'NO2': [20],
        'CO2': [30]
    })
    filename = "test.csv"

    records, validation_errors = validate_records(df, filename)

    assert len(records) == 0
    assert len(validation_errors) > 0


def test_create_db_records():
    records = [
        AirQualityBase(
            date=datetime.date(2023, 1, 1),
            city='TestCity',
            pm2_5=10,
            no2=20,
            co2=30
        )
    ]

    db_records, alert_records = create_db_records(records)

    assert len(db_records) == 1
    assert isinstance(db_records[0], AirQuality)
    assert db_records[0].city == 'TestCity'


def test_create_db_records_with_high_aqi():
    records = [
        AirQualityBase(
            date=datetime.date(2023, 1, 1),
            city='TestCity',
            pm2_5=500,
            no2=200,
            co2=500
        )
    ]

    db_records, alert_records = create_db_records(records)

    assert len(db_records) == 1
    assert len(alert_records) == 1
    assert isinstance(alert_records[0], Alert)


def test_save_records_to_db(mocker):
    mock_db = mocker.Mock()
    db_records = [
        AirQuality(
            date=datetime.date(2023, 1, 1),
            city='TestCity',
            pm2_5=10,
            no2=20,
            co2=30,
            aqi=50,
            aqi_level='Moderate'
        )
    ]
    alert_records = [
        Alert(
            date=datetime.date(2023, 1, 1),
            city='TestCity',
            aqi=350,
            aqi_level='Hazardous'
        )
    ]

    save_records_to_db(mock_db, db_records, alert_records)

    mock_db.bulk_save_objects.assert_called()
    mock_db.commit.assert_called_once()


def test_save_records_to_db_error(mocker):
    mock_db = mocker.Mock()
    mock_db.commit.side_effect = Exception("Database error")

    db_records = [
        AirQuality(
            date=datetime.date(2023, 1, 1),
            city='TestCity',
            pm2_5=10,
            no2=20,
            co2=30,
            aqi=50,
            aqi_level='Moderate'
        )
    ]
    alert_records = []

    with pytest.raises(Exception):
        save_records_to_db(mock_db, db_records, alert_records)

    mock_db.rollback.assert_called_once()