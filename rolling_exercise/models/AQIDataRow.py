import datetime
from dataclasses import dataclass
from typing import Tuple


@dataclass
class AQIDataRow:
    date: datetime.date
    overall_aqi: int
    aqi_level: str

    @classmethod
    def from_results(cls, results: Tuple[int, str, datetime.date]) -> "AQIDataRow":
        return cls(*results)
