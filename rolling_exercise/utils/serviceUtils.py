from datetime import datetime
import re

from settings import settings


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
