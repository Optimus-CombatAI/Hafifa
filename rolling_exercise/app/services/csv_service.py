from io import BytesIO

import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from app.constants.csv_constants import (
    CSV_ENCODING,
    CSV_DATE_COL,
    CSV_CITY_COL,
    CSV_PM25_COL,
    CSV_NO2_COL,
    CSV_CO2_COL,
    REQUIRED_CSV_COLUMNS,
    CSV_MISSING_COLUMNS_ERROR,
    INVALID_CSV_FILE_ERROR,
    INVALID_VALUES_ERROR,
    EMPTY_CITY_ERROR,
)
from app.exceptions import CsvParseError
from app.schemas.air_quality import AirQualityRow
import logging
from app.core.logger import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def parse_air_quality_csv(file_content: bytes) -> list[AirQualityRow]:
    df = _read_csv_bytes(file_content)
    _validate_required_columns(df)
    df = _select_relevant_columns(df)
    _normalize_city_column(df)
    _parse_date_column(df)
    _parse_numeric_columns(df)

    records = df.to_dict(orient="records")
    logger.info(f"CSV parsed successfully: {len(records)} valid rows")

    return [
        AirQualityRow(
            date=record[CSV_DATE_COL],
            city=record[CSV_CITY_COL],
            pm25=float(record[CSV_PM25_COL]),
            no2=float(record[CSV_NO2_COL]),
            co2=float(record[CSV_CO2_COL]),
        )
        for record in records
    ]


def _read_csv_bytes(file_content: bytes) -> pd.DataFrame:
    try:
        return pd.read_csv(BytesIO(file_content), encoding=CSV_ENCODING)
    except (EmptyDataError, ParserError, UnicodeDecodeError) as exc:
        logger.warning("CSV parsing failed: invalid or corrupted file")
        raise CsvParseError(INVALID_CSV_FILE_ERROR) from exc


def _validate_required_columns(df: pd.DataFrame) -> None:
    if not REQUIRED_CSV_COLUMNS.issubset(df.columns):
        logger.warning(f"Missing required CSV columns. Found: {list(df.columns)}")
        raise CsvParseError(CSV_MISSING_COLUMNS_ERROR)


def _select_relevant_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df[[CSV_DATE_COL, CSV_CITY_COL, CSV_PM25_COL, CSV_NO2_COL, CSV_CO2_COL]].copy()


def _normalize_city_column(df: pd.DataFrame) -> None:
    df[CSV_CITY_COL] = df[CSV_CITY_COL].astype(str).str.strip()

    if (df[CSV_CITY_COL] == "").any():
        logger.warning("Some rows contain empty city values.")
        raise CsvParseError(EMPTY_CITY_ERROR)


def _parse_date_column(df: pd.DataFrame) -> None:
    try:
        df[CSV_DATE_COL] = pd.to_datetime(df[CSV_DATE_COL], errors="raise").dt.date
    except (ValueError, TypeError) as exc:
        logger.warning("CSV contains invalid numeric or date values")
        raise CsvParseError(INVALID_VALUES_ERROR) from exc


def _parse_numeric_columns(df: pd.DataFrame) -> None:
    try:
        for col in (CSV_PM25_COL, CSV_NO2_COL, CSV_CO2_COL):
            df[col] = pd.to_numeric(df[col], errors="raise")
    except (ValueError, TypeError) as exc:
        logger.warning("CSV contains invalid numeric values")
        raise CsvParseError(INVALID_VALUES_ERROR) from exc
