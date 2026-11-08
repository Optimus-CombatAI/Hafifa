import pytest
from fastapi import status

from tests.api.uploads import upload_rows
from tests.csv_rows import csv_row


def test_date_range_returns_only_records_inside_it(client):
    upload_rows(client, csv_row(date="2024-11-19"), csv_row(date="2024-11-20"))

    response = client.get("/air-quality", params={"start_date": "2024-11-20", "end_date": "2024-11-20"})

    assert response.status_code == status.HTTP_200_OK
    assert [record["date"] for record in response.json()] == ["2024-11-20"]


def test_record_has_pollutants_and_aqi(client):
    upload_rows(client, csv_row(date="2024-11-19"))

    response = client.get("/air-quality", params={"start_date": "2024-11-19", "end_date": "2024-11-19"})

    assert response.status_code == status.HTTP_200_OK
    assert [set(record) for record in response.json()] == [{"date", "city", "pm25", "no2", "co2", "aqi", "aqi_level"}]


def test_date_range_with_start_after_end_is_unprocessable(client):
    response = client.get("/air-quality", params={"start_date": "2024-11-20", "end_date": "2024-11-19"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_by_city_returns_city_records_of_every_day(client):
    upload_rows(
        client,
        csv_row(date="2024-11-19", city="Haifa"),
        csv_row(date="2024-11-20", city="Haifa"),
        csv_row(date="2024-11-19", city="Akko"),
    )

    response = client.get("/air-quality/by-city", params={"city": "Haifa"})

    assert response.status_code == status.HTTP_200_OK
    assert [(record["date"], record["city"]) for record in response.json()] == [
        ("2024-11-19", "Haifa"),
        ("2024-11-20", "Haifa"),
    ]

def test_aqi_average_names_the_city(client):
    upload_rows(client, csv_row(city="Haifa"))

    response = client.get("/air-quality/aqi-average", params={"city": "Haifa"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["city"] == "Haifa"


def test_best_cities_returns_three_by_default(client):
    upload_rows(client, csv_row(city="Haifa"), csv_row(city="Akko"), csv_row(city="Eilat"), csv_row(city="Netanya"))

    response = client.get("/air-quality/best-cities")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3


def test_best_cities_count_can_be_chosen(client):
    upload_rows(client, csv_row(city="Haifa"), csv_row(city="Akko"), csv_row(city="Eilat"), csv_row(city="Netanya"))

    response = client.get("/air-quality/best-cities", params={"count": 4})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 4


def test_best_cities_count_below_one_is_unprocessable(client):
    response = client.get("/air-quality/best-cities", params={"count": 0})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize("url", ["/air-quality/by-city", "/air-quality/aqi-history", "/air-quality/aqi-average"])
def test_unknown_city_is_not_found(client, url):
    upload_rows(client, csv_row(city="Haifa"))

    response = client.get(url, params={"city": "Atlantis"})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No air quality data for Atlantis"}
