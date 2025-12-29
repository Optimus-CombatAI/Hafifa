import pandas as pd
import pytest
from starlette import status

from settings import settings
from utils.serviceUtils import fill_aqi_data
from utils.testUtils import create_random_report, mock_csv_file, get_random_date_from_report, check_equality_alerts_return_value


class TestGetAlertsSince:
    url = f"{settings.BASE_APP_DIR}/alerts/since"

    async def test_get_alerts_since_random(self, client):
        report_df = create_random_report()
        files = mock_csv_file(report_df)
        await client.post(f"{settings.BASE_APP_DIR}/air_quality/upload", files=files)

        random_date = get_random_date_from_report(report_df)
        response = await client.get(self.url + f"?start_date={random_date}")

        assert response.status_code == status.HTTP_200_OK

        fill_aqi_data(report_df)
        wanted_df = report_df[(report_df["date"] > pd.to_datetime(random_date)) & (report_df['overall_aqi'] > 300)]
        response_df = pd.DataFrame(response.json())

        assert check_equality_alerts_return_value(wanted_df, response_df)

    async def test_get_alerts_since_min(self, client):
        report_df = create_random_report()
        files = mock_csv_file(report_df)
        await client.post(f"{settings.BASE_APP_DIR}/air_quality/upload", files=files)

        earliest_date = report_df['date'].min().date()
        response = await client.get(self.url + f"?start_date={earliest_date}")

        assert response.status_code == status.HTTP_200_OK

        fill_aqi_data(report_df)
        wanted_df = report_df[(report_df["date"] > pd.to_datetime(earliest_date)) & (report_df['overall_aqi'] > settings.ALERT_OVERALL_AQI)]
        response_df = pd.DataFrame(response.json())

        assert check_equality_alerts_return_value(wanted_df, response_df)

    async def test_get_alerts_since_max(self, client):
        report_df = create_random_report()
        files = mock_csv_file(report_df)
        await client.post(f"{settings.BASE_APP_DIR}/air_quality/upload", files=files)

        latest_date = report_df['date'].max().date()
        response = await client.get(self.url + f"?start_date={latest_date}")

        assert response.status_code == status.HTTP_200_OK

        fill_aqi_data(report_df)
        wanted_df = report_df[(report_df["date"] > pd.to_datetime(latest_date)) & (
                    report_df['overall_aqi'] > settings.ALERT_OVERALL_AQI)]
        response_df = pd.DataFrame(response.json())

        assert check_equality_alerts_return_value(wanted_df, response_df)

    async def test_get_alerts_since_invalid(self, client):
        report_df = create_random_report()
        files = mock_csv_file(report_df)
        await client.post(f"{settings.BASE_APP_DIR}/air_quality/upload", files=files)

        response = await client.get(self.url + "?start_date=date-1-not")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
