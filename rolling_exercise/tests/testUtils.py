import datetime
from io import BytesIO
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from pathlib import Path
import logging

from models.pollutantsDataFrame import PollutantsDataFrame
from settings import settings

logger = logging.getLogger(__name__)


def mock_csv_file(df: pd.DataFrame) -> Dict[str, Tuple[str, bytes, str]]:
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue()

    return {"file": ("test.csv", csv_bytes, "text/csv")}


def _fill_lognormal_distribution_column(column: pd.Series, median: int, sigma: float) -> pd.Series:
    none_values_mask = column.isna()
    filled_column = column.copy()

    filled_column.loc[none_values_mask] = np.random.lognormal(
        mean=np.log(median),
        sigma=sigma,
        size=none_values_mask.sum()
    ).round().astype(int)

    return filled_column


def _fill_normal_distribution_column(column: pd.Series, mean: int, std: float) -> pd.Series:
    none_values_mask = column.isna()
    filled_column = column.copy()

    filled_column.loc[none_values_mask] = np.random.normal(
        loc=mean,
        scale=std,
        size=none_values_mask.sum()
    ).round().astype(int)

    return filled_column


def _fill_pm2_5(pm2_5_column: pd.Series, pm25_mean: float = np.log(15), pm25_sigma: float = 0.8) -> None:
    none_values_mask = pm2_5_column.isna()

    pm2_5_column.loc[none_values_mask] = np.random.lognormal(mean=pm25_mean, sigma=pm25_sigma,
                                                             size=none_values_mask.sum()).round().astype(int)


def _fill_no2(no2_column: pd.Series, no2_mean: float = np.log(30), no2_sigma: float = 0.7) -> None:
    none_values_mask = no2_column.isna()

    no2_column.loc[none_values_mask] = np.random.lognormal(mean=no2_mean, sigma=no2_sigma,
                                                           size=none_values_mask.sum()).round().astype(int)


def _fill_co2(co2_column: pd.Series, co2_mean: int = 420, co2_std: int = 50) -> None:
    none_values_mask = co2_column.isna()
    random_co2_values = np.random.normal(loc=co2_mean, scale=co2_std, size=none_values_mask.sum()).round().astype(int)
    random_co2_values = np.clip(random_co2_values, 350, None)

    co2_column.loc[none_values_mask] = random_co2_values


def fill_weather_report_by_internet_data(report_df: pd.DataFrame) -> None:
    report_df["PM2.5"] = _fill_lognormal_distribution_column(report_df["PM2.5"], settings.PM25_MEDIAN, settings.PM25_SIGMA)
    report_df["NO2"] = _fill_lognormal_distribution_column(report_df["NO2"], settings.NO2_MEDIAN, settings.NO2_SIGMA)
    report_df["CO2"] = _fill_normal_distribution_column(report_df["CO2"], settings.CO2_MEAN, settings.CO2_STD)


def _get_all_pollutants_data() -> PollutantsDataFrame:
    directory_path = Path(settings.DATA_PATH)
    air_quality_dfs = [pd.read_csv(file_path) for file_path in directory_path.iterdir() if file_path.suffix == ".csv"]
    all_air_quality_df = pd.concat(air_quality_dfs, ignore_index=True)

    pm25_vals = all_air_quality_df["PM2.5"].dropna().values
    no2_vals = all_air_quality_df["NO2"].dropna().values
    co2_vals = all_air_quality_df["CO2"].dropna().values

    return PollutantsDataFrame(pm25_vals, no2_vals, co2_vals)


def _sample_empirical_with_noise(data: pd.DataFrame, size: int, noise_sigma: float = 0.1):
    base_samples = np.random.choice(data, size=size, replace=True)
    noise = np.random.normal(loc=0, scale=noise_sigma * base_samples)
    noisy_samples = base_samples + noise

    return noisy_samples


def _fill_column_with_empirical_noise(column: pd.Series, reference_values: pd.DataFrame, noise_sigma: float = 0.05) -> pd.Series:
    none_values_mask = column.isna()
    filled_column = column.copy()

    filled_column.loc[none_values_mask] = _sample_empirical_with_noise(
        data=reference_values,
        size=none_values_mask.sum(),
        noise_sigma=noise_sigma
    ).round().astype(int)

    return filled_column


def fill_weather_report_by_dataset_data(report_df: pd.DataFrame) -> None:
    pollutants_data = _get_all_pollutants_data()

    report_df["PM2.5"] = _fill_column_with_empirical_noise(report_df["PM2.5"], pollutants_data.pm25_vals)
    report_df["NO2"] = _fill_column_with_empirical_noise(report_df["NO2"], pollutants_data.no2_vals)
    report_df["CO2"] = _fill_column_with_empirical_noise(report_df["CO2"], pollutants_data.co2_vals)


def fill_weather_report(report_df: pd.DataFrame, method: str = "dataset") -> None:
    if method == "internet":
        fill_weather_report_by_internet_data(report_df)
    else:
        logger.info("adding my data")
        fill_weather_report_by_dataset_data(report_df)


def _fill_dates(report_df: pd.DataFrame) -> None:
    start = datetime.datetime(2025, 11, 10)
    end = datetime.datetime(2025, 11, 15)

    days = (end - start).days + 1
    n = len(report_df)

    if n > days:
        raise ValueError("Not enough unique dates in the given range")

    unique_days = np.random.choice(days, size=n, replace=False)
    report_df["date"] = start + pd.to_timedelta(unique_days, unit="D")


def _fill_cities(report_df: pd.DataFrame) -> None:
    random_cities = ['Be\'er Sheva', 'Holon', 'Haifa', 'Tel Aviv', 'Netanya']

    report_df["city"] = np.random.choice(random_cities, size=len(report_df))


def create_random_report(size: int = 5) -> pd.DataFrame:
    column_names = ['date', 'city', 'PM2.5', 'NO2', 'CO2']
    report_df = pd.DataFrame(columns=column_names, index=range(size))

    fill_weather_report(report_df)
    _fill_dates(report_df)
    _fill_cities(report_df)

    return report_df.copy()


def invalidate_date(report_df: pd.DataFrame) -> None:
    report_df["date"] = report_df["date"].astype(object)
    report_df.loc[report_df.index[0], "date"] = "not-1-date"


def create_holes_in_reports(report_df: pd.DataFrame) -> None:
    report_df.loc[report_df.index[0], "PM2.5"] = pd.NaT
    report_df.loc[report_df.index[0], "NO2"] = pd.NaT
    report_df.loc[report_df.index[0], "CO2"] = pd.NaT


def get_random_date_from_report(report_df: pd.DataFrame) -> datetime.date:
    return report_df.loc[report_df.sample(1).index[0], "date"].date()


def get_random_city_from_report(report_df: pd.DataFrame) -> str:
    return report_df.loc[report_df.sample(1).index[0], "city"]


def check_equality_alerts_return_value(wanted_df: pd.DataFrame, got_df: pd.DataFrame) -> bool:
    if wanted_df.shape[0] == 0 or got_df.shape[0] == 0:
        return wanted_df.shape[0] == 0 and got_df.shape[0] == 0

    wanted_df_norm = (
        wanted_df.copy()
        .rename(columns={"city": "city_name"})
    )

    got_df_norm = got_df.copy().drop(columns=[c for c in ["id"] if c in got_df.columns])
    got_df_norm = got_df_norm[wanted_df_norm.columns]

    wanted_df_norm["date"] = pd.to_datetime(wanted_df_norm["date"])
    got_df_norm["date"] = pd.to_datetime(got_df_norm["date"])

    wanted_df_norm = wanted_df_norm.sort_values(
        by=wanted_df_norm.columns.tolist()
    ).reset_index(drop=True)

    got_df_norm = got_df_norm.sort_values(
        by=got_df_norm.columns.tolist()
    ).reset_index(drop=True)

    return wanted_df_norm.equals(got_df_norm)


def check_equality_aqi_statistics_return_value(wanted_df: pd.DataFrame, got_df: pd.DataFrame) -> bool:
    if wanted_df.shape[0] == 0 or got_df.shape[0] == 0:
        return wanted_df.shape[0] == 0 and got_df.shape[0] == 0

    wanted_df_norm = (
        wanted_df.copy()
        .drop(columns=["city", "PM2.5", "NO2", "CO2"])
    )

    got_df_norm = got_df.copy()
    got_df_norm = got_df_norm[wanted_df_norm.columns]

    wanted_df_norm["date"] = pd.to_datetime(wanted_df_norm["date"])
    got_df_norm["date"] = pd.to_datetime(got_df_norm["date"])

    wanted_df_norm = wanted_df_norm.sort_values(
        by=wanted_df_norm.columns.tolist()
    ).reset_index(drop=True)

    got_df_norm = got_df_norm.sort_values(
        by=got_df_norm.columns.tolist()
    ).reset_index(drop=True)

    return wanted_df_norm.equals(got_df_norm)