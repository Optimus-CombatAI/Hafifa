from datetime import datetime
import re

import numpy as np
import pandas as pd

from settings import settings
from utils.calculate_aqi import calculate_aqi


def is_valid_date(date: str) -> bool:
    try:
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        is_matching_pattern = bool(re.match(pattern, date))
        datetime.strptime(date, settings.DATE_FORMAT)

        return is_matching_pattern

    except ValueError as e:
        return False


def get_aqi_level(overall_aqi: int) -> str:

    aqi_thresholds = [
        (50, "Good"),
        (100, "Moderate"),
        (150, "Unhealthy for Sensitive Groups"),
        (200, "Unhealthy"),
        (300, "Very Unhealthy"),
        (500, "Hazardous")
    ]

    return next(level for threshold, level in aqi_thresholds if overall_aqi <= threshold)


def fill_aqi_data(report_data_df: pd.DataFrame) -> None:
    calc_column_aqi = np.vectorize(calculate_aqi)
    report_data_df["overall_aqi"], report_data_df["aqi_level"] = calc_column_aqi(report_data_df["PM2.5"],
                                                                                 report_data_df["NO2"],
                                                                                 report_data_df["CO2"])
    report_data_df["overall_aqi"] = report_data_df["overall_aqi"].astype(int)

