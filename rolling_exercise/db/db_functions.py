from datetime import datetime, timedelta
import random
import re
from typing import Dict

import numpy as np
import pandas as pd
from sqlalchemy import text, select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from consts import ENGINE, LOGGER, META_DATA, SESSION
from db.cities_table import cities
from db.reports_table import reports
from db.alerts_table import alerts
from entities.city import City
from entities.report import Report
from entities.alert import Alert
from entities.airQualityDataRow import AirQualityDataRow
from entities.AQIDataRow import AQIDataRow
from entities.duplicateDataException import DuplicateDataException
from utils.calculate_aqi import calculate_aqi
from utils.utils import get_aqi_level


async def set_up_db() -> None:
    with ENGINE.connect() as conn:
        for table in reversed(META_DATA.sorted_tables):
            conn.execute(text(f"DROP TABLE IF EXISTS {table.name} CASCADE;"))

        conn.commit()

    META_DATA.create_all(ENGINE)


def _get_random_date(start: datetime = datetime(2025, 11, 10), end: datetime = datetime(2025, 11, 15)) -> datetime.date:
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).date()


async def fill_dummy_data() -> None:
    random_cities = ['Be\'er Sheva', 'Holon', 'Haifa', 'Tel Aviv', 'Netanya']
    levels = ["Good", "Moderate", "Unhealthy for Sensitive Groups", "Unhealthy", "Very Unhealthy", "Hazardous"]
    city_stmt = [insert(cities).values(name=city_name) for city_name in random_cities]

    report_stmt = []
    for i in range(5):
        report_stmt.append(
            insert(reports).values(date=_get_random_date(), city_id=random.randint(1, len(random_cities)),
                                   pm2_5=random.randint(1, 10), no2=random.randint(1, 10), co2=random.randint(1, 10),
                                   overall_aqi=random.randint(1, 10), aqi_level=random.choice(levels))
        )

    alert_stmt = []
    for i in range(2):
        alert_stmt.append(
            insert(alerts).values(date=_get_random_date(), city_id=random.randint(1, len(random_cities)),
                                  overall_aqi=random.randint(1, 10), aqi_level=random.choice(levels))
        )

    with ENGINE.connect() as connection:
        for stmt in city_stmt:
            connection.execute(stmt)

        for stmt in report_stmt:
            connection.execute(stmt)

        for stmt in alert_stmt:
            connection.execute(stmt)

        connection.commit()
        LOGGER.info("Inserted successfully with Core.")


def close_session() -> None:
    SESSION.close()


async def get_cities_to_id_map() -> Dict[str, str]:
    existing_cities = SESSION.execute(select(City.id, City.name)).mappings().all()

    existing_map = {row["name"]: row["id"] for row in existing_cities}

    return existing_map


async def insert_cities(city_names_df: pd.DataFrame) -> None:
    city_names_df = city_names_df.rename(columns={"city": "name"})

    stmt = insert(City).values(city_names_df.to_dict(orient="records"))
    stmt = stmt.on_conflict_do_nothing(index_elements=["name"])  # assumes unique(name)

    SESSION.execute(stmt)
    SESSION.commit()


async def _extract_city_name_and_date(error_message: str) -> tuple[str, datetime.date]:

    pattern = r"\((\d{4}-\d{2}-\d{2}),\s*(\d+)\)"
    match = re.search(pattern, error_message)

    if match:
        date = datetime.strptime(match.group(1), '%Y-%m-%d').date()
        city_id = int(match.group(2))

        name_to_id_map = await get_cities_to_id_map()
        city_name = next((k for k, v in name_to_id_map.items() if v == city_id), None)

        return city_name, date


async def insert_reports(reports_df: pd.DataFrame) -> None:
    city_name_to_id_map = await get_cities_to_id_map()

    reports_to_insert = []
    alerts_to_insert = []

    reports_df = reports_df.rename(columns={"city": "name"})

    vectorised_calc_aqi = np.vectorize(calculate_aqi)
    reports_df["overall_aqi"], reports_df["aqi_level"] = vectorised_calc_aqi(reports_df["PM2.5"], reports_df["NO2"],
                                                                             reports_df["CO2"])

    LOGGER.info(reports_df)

    for _, row in reports_df.iterrows():
        city_id = city_name_to_id_map.get(row["name"])

        reports_to_insert.append(
            Report(
                city_id=city_id,
                date=pd.to_datetime(row["date"]).date(),
                pm2_5=int(row["PM2.5"]),
                no2=int(row["NO2"]),
                co2=int(row["CO2"]),
                overall_aqi=int(row["overall_aqi"]),
                aqi_level=row["aqi_level"]
            )
        )

        if row["overall_aqi"] > 300:
            alerts_to_insert.append(
                Alert(
                    date=pd.to_datetime(row["date"]).date(),
                    city_id=city_id,
                    overall_aqi=int(row["overall_aqi"]),
                    aqi_level=row["aqi_level"]
                )
            )
    try:
        SESSION.bulk_save_objects(reports_to_insert)
        SESSION.bulk_save_objects(alerts_to_insert)

    except IntegrityError as e:
        SESSION.rollback()
        pgcode = getattr(e.orig, 'pgcode', None)

        if pgcode == '23505':
            orig = e.orig
            diag = getattr(orig, "diag", None)
            detail_msg = getattr(diag, "message_detail", None)
            city_name, date = await _extract_city_name_and_date(detail_msg)

            raise DuplicateDataException(city_name, date)

    SESSION.commit()


async def get_air_quality_by_time_range(start_date: datetime.date, end_date: datetime.date) -> list[AirQualityDataRow]:
    stmt = (
        select(City.name, Report.date, Report.pm2_5, Report.no2, Report.co2, Report.overall_aqi, Report.aqi_level)
        .select_from(City)
        .join(Report, City.id == Report.city_id)
        .where(
            (Report.date >= start_date) &
            (Report.date <= end_date)
        )
    )

    results = SESSION.execute(stmt).mappings().all()
    data_rows = [AirQualityDataRow(
            city_name=row['name'],
            report_date=row['date'],
            pm2_5_value=row['pm2_5'],
            no2_value=row['no2'],
            co2_value=row['co2'],
            overall_aqi=row["overall_aqi"],
            aqi_level=row["aqi_level"]
        ) for row in results]

    return data_rows


async def get_air_quality_by_city_name(city_name: str) -> list[AirQualityDataRow]:
    stmt = (
        select(City.name, Report.date, Report.pm2_5, Report.no2, Report.co2, Report.overall_aqi, Report.aqi_level)
        .select_from(City)
        .join(Report, City.id == Report.city_id)
        .where(
            (City.name == city_name)
        )
    )

    results = SESSION.execute(stmt).mappings().all()
    data_rows = [AirQualityDataRow(
            city_name=row['name'],
            report_date=row['date'],
            pm2_5_value=row['pm2_5'],
            no2_value=row['no2'],
            co2_value=row['co2'],
            overall_aqi=row["overall_aqi"],
            aqi_level=row["aqi_level"]
        ) for row in results]

    return data_rows


async def get_aqi_history_by_city(city_name: str) -> list[AQIDataRow]:
    stmt = (
        select(City.name, Report.date, Report.pm2_5, Report.no2, Report.co2, Report.overall_aqi, Report.aqi_level)
        .select_from(City)
        .join(Report, City.id == Report.city_id)
        .where(
            (City.name == city_name)
        )
    )

    results = SESSION.execute(stmt).mappings().all()
    data_rows = [AQIDataRow(
            overall_aqi=row["overall_aqi"],
            aqi_level=row["aqi_level"]
        ) for row in results]

    return data_rows


async def get_aqi_avg_by_city(city_name: str) -> AQIDataRow:
    stmt = (
        select(
            City.name,
            func.avg(Report.overall_aqi)
        )
        .select_from(City)
        .join(Report, City.id == Report.city_id)
        .where(City.name == city_name)
        .group_by(City.id)
    )

    results = SESSION.execute(stmt).mappings().all()

    if not results:
        return AQIDataRow(
            overall_aqi=-1,
            aqi_level="undefined"
        )

    overall_aqi = int(results[0]["avg"])
    data_row = AQIDataRow(
            overall_aqi=overall_aqi,
            aqi_level=get_aqi_level(overall_aqi)
        )

    return data_row


async def get_3_best_cities() -> list[str]:
    stmt = (
        select(
            City.name,
            func.max(Report.overall_aqi)
        )
        .select_from(City)
        .join(Report, City.id == Report.city_id)
        .group_by(City.id)
        .order_by(func.max(Report.overall_aqi).desc())
        .limit(3)
    )

    results = SESSION.execute(stmt).mappings().all()
    city_names = [row["name"] for row in results]

    return city_names




if __name__ == '__main__':
    set_up_db()
