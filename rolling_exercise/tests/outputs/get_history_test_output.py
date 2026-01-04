from dataclasses import dataclass

import pandas as pd
from starlette import status


@dataclass
class TestHistoryOutput:
    __test__ = False
    response_code: int
    response_df: pd.DataFrame


response_1 = {
    'date':  ["2025-11-15", "2025-11-14"],
    'overall_aqi': [304, 275],
    'aqi_level': ['Hazardous', 'Very Unhealthy']
}

test_history_city_output = TestHistoryOutput(status.HTTP_200_OK, pd.DataFrame(response_1))

response_2 = {

}

test_history_not_existing_city_output = TestHistoryOutput(status.HTTP_404_NOT_FOUND, pd.DataFrame(response_2))
