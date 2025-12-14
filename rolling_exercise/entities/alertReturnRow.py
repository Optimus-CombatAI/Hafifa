from dataclasses import dataclass
from datetime import date


@dataclass
class AlertReturnRow:
    id: int
    date: date
    city_name: str
    overall_aqi: int
    aqi_level: str
