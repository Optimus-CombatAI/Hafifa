from dataclasses import dataclass
from datetime import date


@dataclass
class AirQualityDataRow:
    city_name: str
    report_date: date
    pm2_5_value: int
    no2_value: int
    co2_value: int
    overall_aqi: int
    aqi_level: str
