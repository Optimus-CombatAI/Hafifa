from dataclasses import dataclass


@dataclass
class AQIDataRow:
    overall_aqi: int
    aqi_level: str
