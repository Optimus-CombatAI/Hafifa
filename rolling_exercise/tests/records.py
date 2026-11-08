import datetime

from src.db.air_quality_record import AirQualityRecord
from src.db.alert import Alert


def make_record(
    date: datetime.date = datetime.date(2024, 11, 19),
    city: str = "Haifa",
    aqi: float = 50,
    aqi_level: str = "Good",
    with_alert: bool = False,
) -> AirQualityRecord:
    """A valid record. Tests override only the values that matter to them."""
    record = AirQualityRecord(date=date, city=city, pm25=10, no2=20, co2=3, aqi=aqi, aqi_level=aqi_level)

    if with_alert:
        record.alert = Alert(date=date, city=city, aqi=aqi)

    return record
