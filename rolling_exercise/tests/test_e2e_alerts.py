import pytest

CSV_ALERTS = b"""date,city,PM2.5,NO2,CO2
2024-11-19,Tel Aviv,1000,1000,5000
2024-11-20,Tel Aviv,2,2,350
2024-11-20,Jerusalem,1200,1200,6000
"""

@pytest.mark.asyncio
async def test_alerts_returns_list(client):
    resp = await client.get("/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_alerts_by_city_returns_only_that_city(client):
    resp = await client.post("/upload", files={"file": ("air.csv", CSV_ALERTS, "text/csv")})
    assert resp.status_code == 200

    resp = await client.get("/alerts/city/Tel Aviv")
    assert resp.status_code == 200
    data = resp.json()

    assert isinstance(data, list)
    for item in data:
        assert item["city"] == "Tel Aviv"
