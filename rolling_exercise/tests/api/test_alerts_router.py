import pytest
from fastapi import status

from tests.api.uploads import upload_rows
from tests.csv_rows import csv_row

# Above the highest CO2 breakpoint of the given AQI function, so the row gets the maximum AQI of 500
CO2_GIVING_MAX_AQI = "450"


def test_only_rows_over_the_threshold_become_alerts(client):
    upload_rows(
        client,
        csv_row(date="2024-11-19", city="Haifa"),
        csv_row(date="2024-11-19", city="Akko", co2=CO2_GIVING_MAX_AQI),
    )

    response = client.get("/alerts")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"date": "2024-11-19", "city": "Akko", "aqi": 500}]


def test_alerts_by_date_returns_only_that_date(client):
    upload_rows(
        client,
        csv_row(date="2024-11-19", co2=CO2_GIVING_MAX_AQI),
        csv_row(date="2024-11-20", co2=CO2_GIVING_MAX_AQI),
    )

    response = client.get("/alerts/by-date", params={"date": "2024-11-20"})

    assert response.status_code == status.HTTP_200_OK
    assert [alert["date"] for alert in response.json()] == ["2024-11-20"]


def test_alerts_by_city_returns_only_that_city(client):
    upload_rows(
        client,
        csv_row(city="Haifa", co2=CO2_GIVING_MAX_AQI),
        csv_row(city="Akko", co2=CO2_GIVING_MAX_AQI),
    )

    response = client.get("/alerts/by-city", params={"city": "Haifa"})

    assert response.status_code == status.HTTP_200_OK
    assert [alert["city"] for alert in response.json()] == ["Haifa"]


@pytest.mark.parametrize("city", ["Haifa", "Atlantis"], ids=["city with clean air", "unknown city"])
def test_city_without_alerts_gets_empty_list(client, city):
    upload_rows(client, csv_row(city="Haifa"))

    response = client.get("/alerts/by-city", params={"city": city})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_invalid_date_is_unprocessable(client):
    response = client.get("/alerts/by-date", params={"date": "2024-13-45"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
