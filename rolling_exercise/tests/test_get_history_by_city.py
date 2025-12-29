import string
import random

import pandas as pd
import pytest
from starlette import status

from settings import settings
from utils.serviceUtils import fill_aqi_data
from utils.testUtils import create_random_report, mock_csv_file, get_random_city_from_report, check_equality_aqi_statistics_return_value


def _get_random_string(n):
    chars = string.ascii_letters
    return ''.join(random.choices(chars, k=n))


class TestGetHistoryByCity:
    url = f"{settings.BASE_APP_DIR}/aqi_statistics/history"

    @pytest.mark.asyncio
    async def test_get_history_by_random_city(self, client):
        report_df = create_random_report()
        files = mock_csv_file(report_df)
        await client.post(f"{settings.BASE_APP_DIR}/air_quality/upload", files=files)

        random_city = get_random_city_from_report(report_df)
        response = await client.get(self.url + f"?city_name={random_city}")
        assert response.status_code == status.HTTP_200_OK

        response_df = pd.DataFrame(response.json())
        fill_aqi_data(report_df)
        wanted_df = report_df[report_df["city"] == random_city]

        assert check_equality_aqi_statistics_return_value(wanted_df, response_df)

    @pytest.mark.asyncio
    async def test_get_history_not_existing_city(self, client):
        report_df = create_random_report()
        files = mock_csv_file(report_df)
        await client.post(f"{settings.BASE_APP_DIR}/air_quality/upload", files=files)

        random_string = _get_random_string(15)
        response = await client.get(self.url + f"?city_name={random_string}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
