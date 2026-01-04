from typing import List

import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.dml import Insert

from db.pgDatabase import PGDatabase
from entities.city import City
from entities.report import Report
from utils.serviceUtils import fill_aqi_data


def insert_cities_stmt(city_names_df: pd.DataFrame) -> Insert:
    city_names_df = city_names_df.rename(columns={"city": "name"})
    city_names_df["id"] = city_names_df.groupby("name").ngroup()

    stmt = insert(City).values(city_names_df.to_dict(orient="records"))
    stmt = stmt.on_conflict_do_nothing(index_elements=["name"])

    return stmt


def insrt_reports_stmt(report_df: pd.DataFrame) -> List[Insert]:
    report_data_df = report_df.rename(columns={"city": "name"})
    report_data_df["city_id"] = report_data_df.groupby("name").ngroup()

    fill_aqi_data(report_data_df)
    stmts = []

    for _, report_row in report_data_df.iterrows():
        stmt = insert(Report).values(
                date=report_row["date"],
                city_id=report_row["city_id"],
                pm2_5=int(report_row["PM2.5"]),
                no2=int(report_row["NO2"]),
                co2=int(report_row["CO2"]),
                overall_aqi=int(report_row["overall_aqi"]),
                aqi_level=report_row["aqi_level"]
                )
        stmts.append(stmt)

    return stmts


async def insert_data_manually(test_db: PGDatabase, report_df: pd.DataFrame):
    await test_db.execute_with_no_results(insert_cities_stmt(report_df[["city"]]))

    report_stmts = insrt_reports_stmt(report_df)

    for stmt in report_stmts:
        await test_db.execute_with_no_results(stmt)
