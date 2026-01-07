import csv
import io
from datetime import date as DateType

from app.constants.csv_constants import (
    CSV_ENCODING,
    CSV_DATE_COL,
    CSV_CITY_COL,
    CSV_PM25_COL,
    CSV_NO2_COL,
    CSV_CO2_COL,
    REQUIRED_CSV_COLUMNS,
    CSV_MISSING_COLUMNS_ERROR,
)


def parse_air_quality_csv(file_content: bytes) -> list[dict]:
    text = file_content.decode(CSV_ENCODING)
    reader = csv.DictReader(io.StringIO(text))#transforms each line into a dictionary
    fieldnames = set(reader.fieldnames or [])
    if not REQUIRED_CSV_COLUMNS.issubset(fieldnames):
        raise ValueError(CSV_MISSING_COLUMNS_ERROR)

    rows: list[dict] = []

    for row in reader:
        try:
            parsed_row = {
                "date": DateType.fromisoformat(row[CSV_DATE_COL]),
                "city": row[CSV_CITY_COL].strip(),
                "pm25": float(row[CSV_PM25_COL]),
                "no2": float(row[CSV_NO2_COL]),
                "co2": float(row[CSV_CO2_COL]),
            }
            rows.append(parsed_row)

        except (ValueError, TypeError, KeyError):
            continue

    return rows
