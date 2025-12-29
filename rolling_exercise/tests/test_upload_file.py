import pytest
from starlette import status

from settings import settings
from utils.testUtils import create_random_report, mock_csv_file, invalidate_date, create_holes_in_reports


class TestUploadFile:
    url = f"{settings.BASE_APP_DIR}/air_quality/upload"

    async def test_upload_file(self, client):
        report_df = create_random_report()
        files = mock_csv_file(report_df)

        response = await client.post(self.url, files=files)
        assert response.status_code == status.HTTP_201_CREATED

    async def test_double_upload(self, client):
        report_df = create_random_report()
        files = mock_csv_file(report_df)

        response_1 = await client.post(self.url, files=files)
        assert response_1.status_code == status.HTTP_201_CREATED

        response_2 = await client.post(self.url, files=files)
        assert response_2.status_code == status.HTTP_400_BAD_REQUEST

    async def test_invalid_dates(self, client):
        report_df = create_random_report()
        invalidate_date(report_df)
        files = mock_csv_file(report_df)

        response = await client.post(self.url, files=files)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_missing_data(self, client):
        report_df = create_random_report()
        create_holes_in_reports(report_df)
        files = mock_csv_file(report_df)

        response = await client.post(self.url, files=files)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
