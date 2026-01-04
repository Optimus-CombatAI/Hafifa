from dataclasses import dataclass

import pandas as pd
from starlette import status


@dataclass
class TestAlertsOutput:
    __test__ = False
    response_code: int
    response_df: pd.DataFrame


response_1 = {
    'id': [3],
    'date':  ["2025-11-15"],
    'city_name': ['Tel Aviv'],
    'overall_aqi': [304],
    'aqi_level': ['Hazardous']
}

test_random_output = TestAlertsOutput(status.HTTP_200_OK, pd.DataFrame(response_1))

response_2 = {
    'id': [1, 3],
    'date':  ["2025-11-12", "2025-11-11"],
    'city_name': ['Haifa', "Holon"],
    'overall_aqi': [324, 322],
    'aqi_level': ['Hazardous', "Hazardous"]
}

test_min_date_output = TestAlertsOutput(status.HTTP_200_OK, pd.DataFrame(response_2))

response_3 = {

}

test_max_date_output = TestAlertsOutput(status.HTTP_200_OK, pd.DataFrame(response_3))

test_invalid_output = TestAlertsOutput(status.HTTP_400_BAD_REQUEST, pd.DataFrame(response_3))
