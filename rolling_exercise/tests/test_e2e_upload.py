import pytest

CSV_OK = b"""date,city,PM2.5,NO2,CO2
2024-11-19,Tel Aviv,10,20,400
2024-11-20,Tel Aviv,30,40,420
2024-11-20,Jerusalem,15,25,410
"""

@pytest.mark.asyncio(loop_scope="session")
async def test_upload_then_city_endpoint_returns_rows(client):
    files = {"file":("air_quality.csv",CSV_OK,"text/csv")}
    resp = await client.post("/upload",files=files)
    assert resp.status_code == 200
    resp = await client.get("/cities/Tel Aviv")
    assert resp.status_code == 200

    data = resp.json()  
    assert isinstance(data, list)
    assert len(data)
    assert all(row["city"]=="Tel Aviv" for row in data)  
