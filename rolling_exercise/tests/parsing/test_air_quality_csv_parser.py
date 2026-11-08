import datetime

import pytest

from src.errors import InvalidCsvFileError
from src.models.air_quality_reading import AirQualityReading
from src.parsing.air_quality_csv_parser import AirQualityCsvParser
from tests.csv_rows import csv_row, to_csv


def test_valid_row_becomes_reading():
    parsed = AirQualityCsvParser().parse(to_csv("2024-11-19,Haifa,12,40,3"))

    assert parsed.readings == [
        AirQualityReading(line_number=2, date=datetime.date(2024, 11, 19), city="Haifa", pm25=12, no2=40, co2=3)
    ]
    assert parsed.rejected_rows == []


def test_zero_pollutant_values_are_valid():
    parsed = AirQualityCsvParser().parse(to_csv(csv_row(pm25="0", no2="0", co2="0")))

    assert len(parsed.readings) == 1
    assert parsed.rejected_rows == []


@pytest.mark.parametrize(
    ("row", "rejected_column"),
    [
        (csv_row(co2="NaN"), "CO2"),
        (csv_row(no2=""), "NO2"),
        (csv_row(pm25="-1"), "PM2.5"),
        (csv_row(pm25="abc"), "PM2.5"),
        (csv_row(date="2024-13-45"), "date"),
        (csv_row(city=""), "city"),
    ],
)
def test_invalid_value_rejects_row_and_names_the_column(row, rejected_column):
    parsed = AirQualityCsvParser().parse(to_csv(row))

    assert parsed.readings == []
    assert len(parsed.rejected_rows) == 1
    assert parsed.rejected_rows[0].reason.startswith(f"{rejected_column}:")


def test_invalid_row_does_not_stop_valid_rows():
    parsed = AirQualityCsvParser().parse(to_csv(csv_row(city="Haifa"), csv_row(city="Akko", no2="")))

    assert [reading.city for reading in parsed.readings] == ["Haifa"]
    assert [rejected_row.line_number for rejected_row in parsed.rejected_rows] == [3]


@pytest.mark.parametrize(
    ("file_content", "expected_message"),
    [
        (b"", "File is empty"),
        (b"date,city,PM2.5\n2024-11-19,Haifa,12", "Missing columns: NO2, CO2"),
        (b"\xff\xfe\x00not text", "File is not a UTF-8 text file"),
    ],
)
def test_unusable_file_raises(file_content, expected_message):
    with pytest.raises(InvalidCsvFileError, match=expected_message):
        AirQualityCsvParser().parse(file_content)
