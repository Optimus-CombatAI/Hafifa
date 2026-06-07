import pytest

from app.services.aqi_service import calculate_aqi_data

CSV_MIX = b"""date,city,PM2.5,NO2,CO2
2024-11-19,Tel Aviv,10,20,400
2024-11-20,Tel Aviv,30,40,420
2024-11-20,Jerusalem,15,25,410
"""

@pytest.mark.asyncio
async def test_city_unknown_returns_404(client):
    resp = await client.get("/cities/THIS_CITY_DOES_NOT_EXIST")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_city_average_matches_expected(client):
    resp = await client.post("/upload", files={"file": ("air.csv", CSV_MIX, "text/csv")})
    assert resp.status_code == 200

    aqi1 = calculate_aqi_data(pm25=10, no2=20, co2=400).aqi
    aqi2 = calculate_aqi_data(pm25=30, no2=40, co2=420).aqi
    expected_avg = (aqi1 + aqi2) / 2

    resp = await client.get("/cities/Tel Aviv/average")
    assert resp.status_code == 200
    data = resp.json()

    assert data["city"] == "Tel Aviv"
    assert isinstance(data["average_aqi"], (int, float))
    assert data["average_aqi"] == pytest.approx(expected_avg, rel=1e-6)


@pytest.mark.asyncio
async def test_best_cities_are_sorted_by_average_aqi(client):
    csv = b"""date,city,PM2.5,NO2,CO2
2024-11-19,GoodCity,1,1,350
2024-11-19,MidCity,50,50,600
2024-11-19,BadCity,200,200,2000
"""

    resp = await client.post("/upload", files={"file": ("air.csv", csv, "text/csv")})
    assert resp.status_code == 200

    expected = []
    for city, pm25, no2, co2 in [
        ("GoodCity", 1, 1, 350),
        ("MidCity", 50, 50, 600),
        ("BadCity", 200, 200, 2000),
    ]:
        expected.append((city, calculate_aqi_data(pm25=pm25, no2=no2, co2=co2).aqi))

    expected_sorted = sorted(expected, key=lambda x: (x[1],x[0]))
    expected_cities = [c for c, _ in expected_sorted]

    resp = await client.get("/cities/best")
    assert resp.status_code == 200
    data = resp.json()

    assert isinstance(data, list)
    assert len(data) == 3
    got_cities = [item["city"] for item in data]
    assert got_cities == expected_cities

    got_avgs = [item["average_aqi"] for item in data]
    assert got_avgs == sorted(got_avgs)
