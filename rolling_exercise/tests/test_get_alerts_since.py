import pandas as pd
import pytest
from httpx import AsyncClient

from consts import BASE_APP_URL
from db.pgDatabase import PGDatabase
from tests.inputs.get_alerts_since_test_input import test_random_input, test_min_date_input, test_max_date_input, test_invalid_input, TestAlertsInput
from tests.outputs.get_alerts_since_test_output import test_random_output, test_min_date_output, test_max_date_output, test_invalid_output, TestAlertsOutput
from tests.insert_utilities import insert_data_manually


class TestGetAlertsSince:
    url = f"{BASE_APP_URL}/alerts/since"

    @pytest.mark.parametrize(
        "test_input, test_output",
        [
            (test_random_input, test_random_output),
            (test_min_date_input, test_min_date_output),
            (test_max_date_input, test_max_date_output),
            (test_invalid_input, test_invalid_output),
        ],
        ids=["random_input", "min_date", "max_date", "invalid_date"],
    )
    async def test_get_alerts_since(self, test_db: PGDatabase, client: AsyncClient, test_input: TestAlertsInput, test_output: TestAlertsOutput) -> None:
        report_df = test_input.report_df
        await insert_data_manually(test_db, report_df)

        response = await client.get(self.url + f"?start_date={test_input.date}")

        assert response.status_code == test_output.response_code

        if not isinstance(response.json(), dict):
            response_df = pd.DataFrame(response.json())

            assert test_output.response_df.equals(response_df)
