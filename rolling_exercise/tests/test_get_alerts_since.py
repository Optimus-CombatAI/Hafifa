import pytest
from starlette import status

from settings import settings
from utils.testUtils import create_random_report, mock_csv_file


class TestGetAlerts:
    route = "alerts"

    @pytest.mark.asyncio
    async def test_upload_file(self, client):
        report_df = create_random_report()
        files = _mock_csv_file(report_df)

        response = await client.post(f"{settings.BASE_APP_DIR}/{self.route}/upload", files=files)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_double_upload(self, client):
        report_df = create_random_report()
        files = _mock_csv_file(report_df)

        response_1 = await client.post(f"{settings.BASE_APP_DIR}/{self.route}/upload", files=files)
        assert response_1.status_code == status.HTTP_201_CREATED

        response_2 = await client.post(f"{settings.BASE_APP_DIR}/{self.route}/upload", files=files)
        assert response_2.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_invalid_dates(self, client):
        report_df = create_random_report()
        invalidate_date(report_df)
        files = _mock_csv_file(report_df)

        response = await client.post(f"{settings.BASE_APP_DIR}/{self.route}/upload", files=files)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_missing_data(self, client):
        report_df = create_random_report()
        create_holes_in_reports(report_df)
        files = _mock_csv_file(report_df)

        response = await client.post(f"{settings.BASE_APP_DIR}/{self.route}/upload", files=files)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

