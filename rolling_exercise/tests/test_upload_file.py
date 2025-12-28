import pytest
from starlette import status
from starlette.testclient import TestClient

from db.database import Database
from app.main import create_app
from settings import settings
from utils.testUtils import create_random_report, _mock_csv_file


class TestUploadFile:
    route = "air_quality"

    @pytest.mark.asyncio
    async def test_upload_file(self, client):
        report_df = create_random_report()
        files = _mock_csv_file(report_df)

        response = await client.post(f"{settings.BASE_APP_DIR}/{self.route}/upload", files=files)
        if response.status_code != status.HTTP_201_CREATED:
            print(f"\nServer Error Details: {response.json()}")

        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_double_upload(self, client):
        report_df = create_random_report()
        files = _mock_csv_file(report_df)

        response_1 = await client.post(f"{settings.BASE_APP_DIR}/{self.route}/upload", files=files)
        if response_1.status_code != status.HTTP_201_CREATED:
            print(f"\nFirst Server Error Details: {response_1.json()}")

        assert response_1.status_code == status.HTTP_201_CREATED

        response_2 = await client.post(f"{settings.BASE_APP_DIR}/{self.route}/upload", files=files)
        if response_2.status_code != status.HTTP_400_BAD_REQUEST:
            print(f"\nSecond Server Error Details: {response_2.json()}")

        assert response_2.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_invalid_dates(self, client):
        pass


    @pytest.mark.asyncio
    async def test_missing_data(self, client):
        pass
