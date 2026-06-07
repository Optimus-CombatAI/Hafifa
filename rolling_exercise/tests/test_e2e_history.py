import pytest

CSV_HISTORY = b"""date,city,PM2.5,NO2,CO2
2024-11-01,Tel Aviv,10,20,400
2024-11-10,Tel Aviv,30,40,420
2024-12-01,Jerusalem,15,25,410
"""

@pytest.mark.asyncio
async def test_history_invalid_dates_returns_400(client):
    resp = await client.get("/history", params={"start_date": "2024-12-10", "end_date": "2024-12-01"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_history_filters_by_date_range(client):
    resp = await client.post("/upload", files={"file": ("air.csv", CSV_HISTORY, "text/csv")})
    assert resp.status_code == 200

    resp = await client.get("/history", params={"start_date": "2024-11-01", "end_date": "2024-11-30"})
    assert resp.status_code == 200
    data = resp.json()

    dates = [row["date"] for row in data]
    assert "2024-11-01" in dates
    assert "2024-11-10" in dates
    assert "2024-12-01" not in dates
