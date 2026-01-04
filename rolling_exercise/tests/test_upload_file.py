import pytest
from starlette import status

from conftest import settings
from inputs.upload_test_input import test_valid_data_input, test_invalid_dates_input, test_missing_data_input
from outputs.upload_test_output import test_valid_data_output, test_invalid_dates_output, test_missing_data_output
from tests.testUtils import mock_csv_file


class TestUploadFile:
    url = f"{settings.BASE_APP_URL}/air_quality/upload"

    @pytest.mark.parametrize(
        "report_df, expected_status",
        [
            (test_valid_data_input, test_valid_data_output),
            (test_invalid_dates_input, test_invalid_dates_output),
            (test_missing_data_input, test_missing_data_output),
        ],
        ids=["valid_input", "invalid_dates", "missing_data"],
    )
    async def test_upload_file(self, client, report_df, expected_status):
        files = mock_csv_file(report_df)

        response = await client.post(self.url, files=files)
        assert response.status_code == expected_status

    async def test_double_upload(self, client):
        report_df = test_valid_data_input
        files = mock_csv_file(report_df)

        response_1 = await client.post(self.url, files=files)
        assert response_1.status_code == status.HTTP_201_CREATED

        response_2 = await client.post(self.url, files=files)
        assert response_2.status_code == status.HTTP_400_BAD_REQUEST
