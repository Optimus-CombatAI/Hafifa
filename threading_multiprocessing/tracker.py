import datetime
import os
from yahoo_fin import stock_info
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from itertools import chain


BITCOIN_FILE_PATH = os.getenv("BITCOIN_DATES", "bitcoin_dates.txt")
AMAZON_FILE_PATH = os.getenv("AMAZON_DATES", "amazon_dates.txt")
GOOGLE_FILE_PATH = os.getenv("GOOGLE_DATES", "google_date.txt")
DESTINATION_FILE_PATH = os.getenv("DESTINATION_FILE", "stock_data.csv")


def get_timestamps(file_path):
    try:
        with open(file_path, 'r') as file:
            return [datetime.datetime.strptime(line.strip(), "%Y-%m-%d %H:%M:%S.%f").date() for line in file]
    except Exception as error:
        print(f"Error reading file: {error}")
        return []


def fetch_stock_data(stock_symbol, stock_type, timestamp):
    start_date = datetime.datetime.combine(timestamp, datetime.time.min)
    end_date = start_date + datetime.timedelta(days=1)

    ticker_history = stock_info.get_data(stock_symbol, start_date=start_date, end_date=end_date)
    stock_data = ticker_history.iloc[0]
    open_price = stock_data["open"]
    close_price = stock_data["close"]

    return {
        "hour": start_date,
        "type": stock_type,
        "percentage_change": ((close_price - open_price) / open_price) * 100,
    }


def gather_stock_data(timestamps_by_symbol):
    tasks = chain(
        (("BTC-USD", "Bitcoin", timestamp) for timestamp in timestamps_by_symbol["bitcoin"]),
        (("AMZN", "Amazon", timestamp) for timestamp in timestamps_by_symbol["amazon"]),
        (("GOOGL", "Google", timestamp) for timestamp in timestamps_by_symbol["google"]),
    )

    with ThreadPoolExecutor() as executor:
        results = executor.map(lambda args: fetch_stock_data(*args), tasks)

    return list(results)


def save_to_csv(stock_data, file_path):
    df = pd.DataFrame(stock_data)
    df.drop_duplicates(inplace=True)
    df.to_csv(file_path, index=False)


def main():
    timestamps_by_symbol = {
        "bitcoin": get_timestamps(BITCOIN_FILE_PATH),
        "amazon": get_timestamps(AMAZON_FILE_PATH),
        "google": get_timestamps(GOOGLE_FILE_PATH)
    }

    stock_data = gather_stock_data(timestamps_by_symbol)
    save_to_csv(stock_data, DESTINATION_FILE_PATH)


if __name__ == "__main__":
    main()