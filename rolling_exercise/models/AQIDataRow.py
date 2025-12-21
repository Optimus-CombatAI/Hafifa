from dataclasses import dataclass
from typing import Tuple


@dataclass
class AQIDataRow:
    overall_aqi: int
    aqi_level: str

    @classmethod
    def from_results(cls, results: Tuple[int, str]) -> "AQIDataRow":
        return cls(*results)
