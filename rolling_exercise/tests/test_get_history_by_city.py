import string
import random

import pandas as pd
import pytest
from httpx import AsyncClient

from consts import BASE_APP_URL
from db.pgDatabase import PGDatabase
from tests.inputs.get_history_test_input import test_history_city_input, test_history_not_existing_city_input, TestHistoryInput
from tests.insert_utilities import insert_data_manually
from tests.outputs.get_history_test_output import test_history_city_output, test_history_not_existing_city_output, TestHistoryOutput


class TestGetHistoryByCity:
    url = f"{BASE_APP_URL}/aqi_statistics/history"

    @pytest.mark.parametrize(
        "test_input, test_output",
        [
            (test_history_city_input, test_history_city_output),
            (test_history_not_existing_city_input, test_history_not_existing_city_output)
        ],
        ids=["random_city", "not_existing_city"],
    )
    async def test_get_history_by_city(self, test_db: PGDatabase, client: AsyncClient, test_input: TestHistoryInput, test_output: TestHistoryOutput) -> None:
        report_df = test_input.report_df
        await insert_data_manually(test_db, report_df)

        response = await client.get(self.url + f"?city_name={test_input.city}")

        assert response.status_code == test_output.response_code

        if not isinstance(response.json(), dict):
            response_df = pd.DataFrame(response.json())
            print("response:\n", response_df)
            assert test_output.response_df.equals(response_df)
