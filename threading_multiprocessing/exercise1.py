import os
import pandas as pd
import yfinance as yf
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from consts import HOURS_FILE_ENV, DESTINATION_FILE_ENV


logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_hours_from_file(file_path: str) -> pd.DataFrame:
    """
    Load hours from a text file using pandas.
    Returns a DataFrame with a single column named 'hour'.
    """
    df = pd.read_csv(file_path, header=None, names=["hour"])
    df.dropna(inplace=True)
    df["hour"] = df["hour"].astype(str)
    return df


def fetch_bitcoin_price_at(timestamp: str) -> float | None:
    """
    Fetch Bitcoin price for a specific timestamp using Yahoo Finance.
    """
    dt_start = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    dt_end = dt_start + timedelta(hours=1)
    data = yf.Ticker("BTC-USD").history(start=dt_start, end=dt_end)

    if data.empty:
        return None

    return float(data["Close"].iloc[0])


def fetch_prices_with_threads(hours_df: pd.DataFrame) -> pd.DataFrame:
    """
    Fetch Bitcoin prices in parallel using ThreadPoolExecutor.
    Returns a DataFrame with columns: 'hour' and 'price'.
    """
    results = []

    with ThreadPoolExecutor() as executor:
        future_to_hour = {
            executor.submit(fetch_bitcoin_price_at, hour): hour
            for hour in hours_df["hour"]
        }

        for future, hour in future_to_hour.items():
            price = future.result()
            results.append({"hour": hour, "price": price})

    return pd.DataFrame(results)


def calculate_percentage_changes(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate percentage change using pandas vectorized operations.
    """
    prices_df = prices_df.sort_values("hour").reset_index(drop=True)
    prices_df["previous_hour"] = prices_df["hour"].shift(1)
    prices_df["previous_price"] = prices_df["price"].shift(1)

    prices_df["percentage_change"] = (
        (prices_df["price"] - prices_df["previous_price"]) /
        prices_df["previous_price"] * 100
    )

    prices_df["percentage_change"] = prices_df["percentage_change"].round(4)
    prices_df.dropna(inplace=True)

    return prices_df[
        ["hour", "price", "previous_hour", "previous_price", "percentage_change"]
    ]


def save_to_csv(df: pd.DataFrame, destination_path: str) -> None:
    """
    Save the DataFrame to a CSV file.
    """
    df.to_csv(destination_path, index=False)


def main():
    """
    Main pipeline:
    - Load hours
    - Fetch Bitcoin prices in parallel
    - Compute percentage change using pandas
    - Save results into CSV
    """

    hours_file_path = os.getenv(HOURS_FILE_ENV)
    destination_file_path = os.getenv(DESTINATION_FILE_ENV)

    if not hours_file_path:
        logger.error("ERROR: HOURS_FILE is missing")
        raise RuntimeError("Environment variable HOURS_FILE is missing")

    if not destination_file_path:
        logger.error("ERROR: DESTINATION_FILE is missing")
        raise RuntimeError("Environment variable DESTINATION_FILE_ENV is missing")

    hours_df = load_hours_from_file(hours_file_path)
    prices_df = fetch_prices_with_threads(hours_df)
    results_df = calculate_percentage_changes(prices_df)
    save_to_csv(results_df, destination_file_path)


if __name__ == "__main__":
    main()
