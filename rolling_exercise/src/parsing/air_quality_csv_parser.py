import csv
import io
import logging

from pydantic import ValidationError

from src.errors import InvalidCsvFileError
from src.models.air_quality_reading import AirQualityReading
from src.models.parsed_upload import ParsedUpload
from src.models.rejected_row import RejectedRow

logger = logging.getLogger(__name__)

FIELD_BY_COLUMN = {"date": "date", "city": "city", "PM2.5": "pm25", "NO2": "no2", "CO2": "co2"}
COLUMN_BY_FIELD = {field: column for column, field in FIELD_BY_COLUMN.items()}


class AirQualityCsvParser:
    """Turns an uploaded CSV into valid readings, keeping the rows that failed validation and why."""

    def parse(self, file_content: bytes) -> ParsedUpload:
        reader = csv.DictReader(io.StringIO(self._decode(file_content)))
        self._check_columns(reader.fieldnames)

        readings = []
        rejected_rows = []

        for row in reader:
            try:
                readings.append(self._to_reading(row))
            except ValidationError as error:
                rejected_row = RejectedRow(line_number=reader.line_num, reason=self._describe(error))
                logger.warning(f"Rejected line {rejected_row.line_number}: {rejected_row.reason}")
                rejected_rows.append(rejected_row)

        logger.info(f"Parsed {len(readings)} valid rows, rejected {len(rejected_rows)}")

        return ParsedUpload(readings=readings, rejected_rows=rejected_rows)

    def _decode(self, file_content: bytes) -> str:
        try:
            return file_content.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise InvalidCsvFileError("File is not a UTF-8 text file")

    def _check_columns(self, columns: list[str] | None):
        if not columns:
            raise InvalidCsvFileError("File is empty")

        missing_columns = [column for column in FIELD_BY_COLUMN if column not in columns]

        if missing_columns:
            raise InvalidCsvFileError(f"Missing columns: {', '.join(missing_columns)}")

    def _to_reading(self, row: dict[str, str]) -> AirQualityReading:
        return AirQualityReading.model_validate({field: row[column] for column, field in FIELD_BY_COLUMN.items()})

    def _describe(self, error: ValidationError) -> str:
        return "; ".join(f"{COLUMN_BY_FIELD[issue['loc'][0]]}: {issue['msg']}" for issue in error.errors())
