from datetime import datetime
import re

import numpy as np
import pandas as pd
from pathlib import Path


from consts import PM25_MEDIAN, PM25_SIGMA, NO2_MEDIAN, NO2_SIGMA, CO2_MEAN, CO2_STD, DATA_PATH, LOGGER
from entities.pollutantsDataFrame import PollutantsDataFrame


def is_valid_date(date: str) -> bool:
    try:
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        is_matching_pattern = bool(re.match(pattern, date))
        datetime.strptime(date, "%Y-%m-%d")
        return is_matching_pattern

    except ValueError:
        return False


def _fill_lognormal_distribution_column(column: pd.Series, median, sigma) -> pd.Series:
    none_values_mask = column.isna()
    filled_column = column.copy()

    filled_column.loc[none_values_mask] = np.random.lognormal(
        mean=np.log(median),
        sigma=sigma,
        size=none_values_mask.sum()
    ).round().astype(int)

    return filled_column


def _fill_normal_distribution_column(column: pd.Series, mean, std) -> pd.Series:
    none_values_mask = column.isna()
    filled_column = column.copy()

    filled_column.loc[none_values_mask] = np.random.normal(
        loc=mean,
        scale=std,
        size=none_values_mask.sum()
    ).round().astype(int)

    return filled_column


"""
def _fill_pm2_5(pm2_5_column: pd.Series, pm25_mean=np.log(15), pm25_sigma=0.8) -> None:
    # PM2.5 log-normal parameters (approximate)
    pm25_mean = np.log(15)  # pm25_median = 15
    pm25_sigma = 0.8

    none_values_mask = pm2_5_column.isna()

    pm2_5_column.loc[none_values_mask] = np.random.lognormal(mean=pm25_mean, sigma=pm25_sigma,
                                                             size=none_values_mask.sum()).round().astype(int)


def _fill_no2(no2_column: pd.Series) -> None:
    # NO2 log-normal parameters (approximate)
    no2_mean = np.log(30)  # no2_median = 30
    no2_sigma = 0.7

    none_values_mask = no2_column.isna()

    no2_column.loc[none_values_mask] = np.random.lognormal(mean=no2_mean, sigma=no2_sigma,
                                                           size=none_values_mask.sum()).round().astype(int)


def _fill_co2(co2_column: pd.Series) -> None:
    # CO2 normal parameters
    co2_mean = 420
    co2_std = 50

    none_values_mask = co2_column.isna()
    random_co2_values = np.random.normal(loc=co2_mean, scale=co2_std, size=none_values_mask.sum()).round().astype(int)
    random_co2_values = np.clip(random_co2_values, 350, None)
    co2_column.loc[none_values_mask] = random_co2_values
"""


def fill_weather_report_by_internet_data(report_df: pd.DataFrame) -> None:
    report_df["PM2.5"] = _fill_lognormal_distribution_column(report_df["PM2.5"], PM25_MEDIAN, PM25_SIGMA)
    report_df["NO2"] = _fill_lognormal_distribution_column(report_df["NO2"], NO2_MEDIAN, NO2_SIGMA)
    report_df["CO2"] = _fill_normal_distribution_column(report_df["CO2"], CO2_MEAN, CO2_STD)


def _get_all_pollutants_data() -> PollutantsDataFrame:
    directory_path = Path(DATA_PATH)  # Replace with your directory path
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


def _fill_column_with_empirical_noise(column: pd.Series, reference_values: pd.DataFrame, noise_sigma=0.05) -> pd.Series:
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


def fill_weather_report(report_df: pd.DataFrame, method="internet") -> None:
    if method == "internet":
        fill_weather_report_by_internet_data(report_df)
    else:
        LOGGER.info("adding my data")
        fill_weather_report_by_dataset_data(report_df)
