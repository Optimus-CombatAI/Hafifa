import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Lock

import pandas as pd
import yfinance as yf


def read_dates(file_path: str) -> list[str]:
    """Read dates from a text file and return them as a list of strings."""
    with open(file_path, "r") as file:
        lines = file.readlines()

    dates = []

    for line in lines:
        date = line.strip()

        if date:
            dates.append(date)

    return dates


def normalize_date(date_str: str) -> datetime:
    """Convert a date string to a UTC datetime rounded down to the hour."""
    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
    date = date.replace(minute=0, second=0, microsecond=0)
    date = date.replace(tzinfo=timezone.utc)

    return date


def get_previous_hour(date_str: str) -> datetime:
    """Return the previous hour as a UTC datetime."""
    return normalize_date(date_str) - timedelta(hours=1)


def calculate_percentage(first_value: float, second_value: float) -> float:
    """Calculate the percentage change between two values."""
    return ((first_value - second_value) / second_value) * 100


def get_hourly_price(data: pd.DataFrame, date: datetime) -> float | None:
    """Return the latest available hourly opening price."""
    index = data.index.asof(date)

    if pd.isna(index) or date - index >= timedelta(hours=1):
        return None

    return float(data["Open"].loc[index])


def calculate_hourly_change(data: pd.DataFrame, date_str: str) -> float | None:
    """Calculate the stock price change over the previous hour."""
    if data.empty:
        return None

    current_price = get_hourly_price(data, normalize_date(date_str))
    previous_price = get_hourly_price(data, get_previous_hour(date_str))

    if current_price is None or previous_price is None:
        return None

    return calculate_percentage(current_price, previous_price)


def get_date_range(dates: list[str]) -> tuple[datetime, datetime]:
    """Return the start and end dates for downloading stock prices."""
    earliest = normalize_date(min(dates))
    latest = normalize_date(max(dates))

    start = earliest - timedelta(days=1)
    end = latest + timedelta(days=1)

    return start, end


def fetch_stock_data(ticker: str, dates: list[str]) -> pd.DataFrame:
    """Fetch hourly stock prices from Yahoo Finance."""
    start, end = get_date_range(dates)

    stock = yf.Ticker(ticker)

    return stock.history(
        start=start,
        end=end,
        interval="1h"
    )


def process_stock(ticker: str, file_path: str, results: list[dict], lock: Lock) -> None:
    """Process stock dates and safely append results to a shared list."""
    dates = read_dates(file_path)
    data = fetch_stock_data(ticker, dates)

    for date in dates:
        percentage = calculate_hourly_change(data, date)

        if percentage is not None:
            with lock:
                results.append({
                    "hour": date,
                    "stock type": ticker,
                    "percentage change": percentage
                })


def run_threads(stocks: dict[str, str]) -> list[dict]:
    """Process multiple stocks concurrently."""
    all_results = []
    lock = Lock()

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(process_stock, ticker, path, all_results, lock)
            for ticker, path in stocks.items()
        ]

        for future in futures:
            future.result()

    return all_results


def save_to_csv(results: list[dict], file_path: str) -> None:
    """Save stock price changes to a CSV file."""
    df = pd.DataFrame(results)
    df.to_csv(file_path, index=False)


def main():
    """Run the stock price mining program."""
    stocks = {
        "BTC-USD": os.environ.get("BITCOIN_DATES"),
        "GOOG": os.environ.get("GOOGLE_DATES"),
        "AMZN": os.environ.get("AMAZON_DATES")
    }

    all_results = run_threads(stocks)

    destination_path = os.environ.get("DESTINATION_FILE")
    save_to_csv(all_results, destination_path)
    print("CSV saved at:", destination_path)


if __name__ == "__main__":
    main()
