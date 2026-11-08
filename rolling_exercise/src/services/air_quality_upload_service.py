import logging

from src.db.air_quality_record import AirQualityRecord
from src.db.alert import Alert
from src.models.air_quality_reading import AirQualityReading
from src.models.rejected_row import RejectedRow
from src.models.upload_report import UploadReport
from src.parsing.air_quality_csv_parser import AirQualityCsvParser
from src.repositories.air_quality_repository import AirQualityRepository
from src.services.aqi_calculator import AqiCalculator

logger = logging.getLogger(__name__)


class AirQualityUploadService:
    """Turns an uploaded CSV into saved air quality records, with an alert for each record over the threshold."""

    def __init__(
        self,
        parser: AirQualityCsvParser,
        calculator: AqiCalculator,
        air_quality_repository: AirQualityRepository,
        alert_aqi_threshold: float,
    ):
        self._parser = parser
        self._calculator = calculator
        self._air_quality_repository = air_quality_repository
        self._alert_aqi_threshold = alert_aqi_threshold

    def upload(self, file_name: str, file_content: bytes) -> UploadReport:
        logger.info(f"Processing upload {file_name}")

        parsed_upload = self._parser.parse(file_content)
        new_readings, duplicate_rows = self._reject_duplicates(parsed_upload.readings)
        records = [self._to_record(reading) for reading in new_readings]
        self._air_quality_repository.save_all(records)

        upload_report = UploadReport(
            saved_rows=len(records),
            created_alerts=sum(record.alert is not None for record in records),
            rejected_rows=sorted(
                parsed_upload.rejected_rows + duplicate_rows, key=lambda rejected_row: rejected_row.line_number
            ),
        )
        logger.info(
            f"Finished upload {file_name}: saved {upload_report.saved_rows} rows, "
            f"created {upload_report.created_alerts} alerts, rejected {len(upload_report.rejected_rows)}"
        )

        return upload_report

    def _reject_duplicates(
        self, readings: list[AirQualityReading]
    ) -> tuple[list[AirQualityReading], list[RejectedRow]]:
        upload_dates = {reading.date for reading in readings}
        taken_city_days = {
            (date, city.lower()) for date, city in self._air_quality_repository.get_city_days(upload_dates)
        }
        new_readings = []
        duplicate_rows = []

        for reading in readings:
            city_day = (reading.date, reading.city.lower())

            if city_day in taken_city_days:
                duplicate_row = RejectedRow(
                    line_number=reading.line_number, reason=f"{reading.city} already has data for {reading.date}"
                )
                logger.warning(f"Rejected line {duplicate_row.line_number}: {duplicate_row.reason}")
                duplicate_rows.append(duplicate_row)
            else:
                taken_city_days.add(city_day)
                new_readings.append(reading)

        return new_readings, duplicate_rows

    def _to_record(self, reading: AirQualityReading) -> AirQualityRecord:
        aqi_result = self._calculator.calculate(reading.pm25, reading.no2, reading.co2)
        record = AirQualityRecord(
            date=reading.date,
            city=reading.city,
            pm25=reading.pm25,
            no2=reading.no2,
            co2=reading.co2,
            aqi=aqi_result.aqi,
            aqi_level=aqi_result.aqi_level,
        )

        if record.aqi > self._alert_aqi_threshold:
            logger.info(f"Alert for {record.city} on {record.date}: AQI {record.aqi}")
            record.alert = Alert(date=record.date, city=record.city, aqi=record.aqi)

        return record
