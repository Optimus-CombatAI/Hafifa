from dataclasses import dataclass
from datetime import date
from typing import Tuple


@dataclass
class AlertReturnRow:
    id: int
    date: date
    city_name: str
    overall_aqi: int
    aqi_level: str

    @classmethod
    def from_report(cls, report: Tuple[int, date, str, int, str]) -> "AlertReturnRow":
        return cls(*report)
