from dataclasses import dataclass

import pandas as pd
from pandas import Timestamp


@dataclass
class TestHistoryInput:
    __test__ = False
    city: str
    report_df: pd.DataFrame


report_1 = {
    'date': [Timestamp('2025-11-13 00:00:00'), Timestamp('2025-11-10 00:00:00'), Timestamp('2025-11-15 00:00:00'), Timestamp('2025-11-14 00:00:00'), Timestamp('2025-11-11 00:00:00')],
    'city': ["Be'er Sheva", "Be'er Sheva", 'Tel Aviv', 'Tel Aviv', 'Haifa'],
    'PM2.5':  [67, 65, 55, 59, 59],
    'NO2': [86, 83, 102, 90, 79],
    'CO2': [427, 418, 447, 440, 448]
}

test_history_city_input = TestHistoryInput("Tel Aviv", pd.DataFrame(report_1))

report_2 = {
    'date': [Timestamp('2025-11-12 00:00:00'), Timestamp('2025-11-15 00:00:00'), Timestamp('2025-11-11 00:00:00'), Timestamp('2025-11-14 00:00:00'), Timestamp('2025-11-10 00:00:00')],
    'city': ['Haifa', 'Haifa', 'Holon', "Be'er Sheva", 'Haifa'],
    'PM2.5':  [53, 66, 71, 68, 75],
    'NO2': [112, 92, 111, 83, 96],
    'CO2': [489, 437, 426, 365, 411]
}

test_history_not_existing_city_input = TestHistoryInput("sdvd", pd.DataFrame(report_2))


