from __future__ import annotations

from io import BytesIO
import pandas as pd

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
from app.schemas.air_quality import AirQualityRow


def parse_air_quality_csv(file_content: bytes) -> list[AirQualityRow]:

    df = pd.read_csv(BytesIO(file_content), encoding=CSV_ENCODING)
    if not REQUIRED_CSV_COLUMNS.issubset(df.columns):
        raise ValueError(CSV_MISSING_COLUMNS_ERROR)

    df = df[[CSV_DATE_COL, CSV_CITY_COL, CSV_PM25_COL, CSV_NO2_COL, CSV_CO2_COL]].copy()
    df[CSV_CITY_COL] = df[CSV_CITY_COL].astype(str).str.strip()
    df[CSV_DATE_COL] = pd.to_datetime(df[CSV_DATE_COL], errors="coerce").dt.date # if invalid ->Nat

    for col in (CSV_PM25_COL, CSV_NO2_COL, CSV_CO2_COL):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=[CSV_DATE_COL, CSV_CITY_COL, CSV_PM25_COL, CSV_NO2_COL, CSV_CO2_COL])

    rows: list[AirQualityRow] = []
    for record in df.to_dict(orient="records"):
        rows.append(
            AirQualityRow(
                date=record[CSV_DATE_COL],
                city=record[CSV_CITY_COL],
                pm25=float(record[CSV_PM25_COL]),
                no2=float(record[CSV_NO2_COL]),
                co2=float(record[CSV_CO2_COL]),
            )
        )

    return rows
