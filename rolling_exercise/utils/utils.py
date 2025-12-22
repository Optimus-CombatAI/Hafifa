from datetime import datetime
import re

import numpy as np
import pandas as pd
import logging
from pathlib import Path

from models.pollutantsDataFrame import PollutantsDataFrame
from settings import settings

logger = logging.getLogger(__name__)


def is_valid_date(date: str) -> bool:
    try:
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        is_matching_pattern = bool(re.match(pattern, date))
        datetime.strptime(date, settings.DATE_FORMAT)

        return is_matching_pattern

    except ValueError as e:
        return False


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


def fill_weather_report(report_df: pd.DataFrame, method: str = "internet") -> None:
    if method == "internet":
        fill_weather_report_by_internet_data(report_df)
    else:
        logger.info("adding my data")
        fill_weather_report_by_dataset_data(report_df)


def get_aqi_level(overall_aqi: int) -> str:

    aqi_thresholds = [
        (50, "Good"),
        (100, "Moderate"),
        (150, "Unhealthy for Sensitive Groups"),
        (200, "Unhealthy"),
        (300, "Very Unhealthy"),
        (500, "Hazardous")
    ]

    return next(level for threshold, level in aqi_thresholds if overall_aqi <= threshold)
