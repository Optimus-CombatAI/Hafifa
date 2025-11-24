import yfinance as yf
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

DESTINATION_FILE = os.getenv("DESTINATION_FILE", "destination.txt")
SOURCE_FILE = os.getenv("SOURCE_FILE", "source.txt")

BTC_TICKER = yf.Ticker("BTC-USD")


def get_dates(file_path: str) -> list[datetime]:
    """
    another possibility
    unique_dates = {line.strip().split()[0] for line in file}
    dates_list = [datetime(*map(int, date.split("-"))) for date in unique_dates]
    """
    with open(file_path) as source_file:
        unique_dates = {line.strip().split()[0] for line in source_file}
        dates_list = []

    for date in unique_dates:
        year, month, day = date.split("-")
        dates_list.append(datetime(int(year), int(month), int(day)))

    return dates_list


def get_next_date(date: datetime) -> datetime:
    return date + timedelta(days=1)


def fetch_data(date, results) -> None:
    data = BTC_TICKER.history(start=date, end=get_next_date(date))
    results[date] = data


def write_to_csv(results: dict) -> None:
    sorted_results = dict(sorted(results.items()))

    combined_df = pd.concat(sorted_results.values())
    combined_df = combined_df.reset_index()

    combined_df["percent_change"] = combined_df["Close"].pct_change() * 100
    combined_df["percent_change"] = combined_df["percent_change"].fillna(0)

    combined_df["stock_type"] = "BTC"

    combined_df[["Date", "stock_type", "percent_change"]].to_csv(DESTINATION_FILE)


def main() -> None:

    dates = get_dates(SOURCE_FILE)

    results = {}

    with ThreadPoolExecutor() as exe:
        for date in dates:
            exe.submit(fetch_data, date, results)

    write_to_csv(results)


if __name__ == '__main__':
    main()
