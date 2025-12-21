from dataclasses import dataclass
from datetime import date

from entities.report import Report


@dataclass
class AirQualityDataRow:
    city_name: str
    report_date: date
    pm2_5_value: int
    no2_value: int
    co2_value: int
    overall_aqi: int
    aqi_level: str

    @classmethod
    def from_report(cls, report: Report) -> "AirQualityDataRow":
        return cls(
            city_name=report.city.name,
            report_date=report.date,
            pm2_5_value=report.pm2_5,
            no2_value=report.no2,
            co2_value=report.co2,
            overall_aqi=report.overall_aqi,
            aqi_level=report.aqi_level
        )
