import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, Future
import yfinance as yf

from pathlib import Path
from constants import SOURCE_FILES, DESTINATION_FILES, STOCK_TICKERS


def prepare_stock_data_df(futures: list[Future]) -> pd.DataFrame:
    stock_results = [future.result() for future in futures if not future.result().empty]
    combined_stock_df = pd.concat(stock_results)

    return combined_stock_df.reset_index()


def clean_up_dates(dates_df: pd.DataFrame) -> pd.DataFrame:
    dates_df['date'] = pd.to_datetime(dates_df['raw_line'], format="%Y-%m-%d %H:%M:%S.%f")
    dates_df['date'] = dates_df['date'].dt.normalize()

    return dates_df[['date']].drop_duplicates().sort_values(by='date').reset_index(drop=True)


def get_stock_type_from_destination_file(file_path: str) -> str:
    """used for getting the stock name for file documentation"""
    no_suffix = Path(file_path).stem

    return no_suffix.replace("_data", "")


def get_dates(file_paths: list[str]) -> list[pd.DataFrame]:
    dates = []

    for file_path in file_paths:
        df = pd.read_csv(file_path, header=None, names=['raw_line'])
        dates.append(clean_up_dates(df))

    return dates


def get_next_date(date: datetime) -> datetime:
    return date + timedelta(days=1)


def fetch_data(date: datetime, ticker: yf.Ticker) -> pd.DataFrame:
    return ticker.history(start=date, end=get_next_date(date))


def add_percentage(dates_df: pd.DataFrame) -> None:
    dates_df["percent_change"] = dates_df["Close"].pct_change() * 100
    dates_df["percent_change"] = dates_df["percent_change"].fillna(0)


def write_to_csv(stock_data: pd.DataFrame, destination_file: str) -> None:
    add_percentage(stock_data)

    stock_data["stock_type"] = get_stock_type_from_destination_file(destination_file)
    stock_data[["Date", "stock_type", "percent_change"]].to_csv(destination_file)


def main() -> None:

    stocks_dates = get_dates(SOURCE_FILES)

    stocks_futures = []

    for stock_dates, stock_ticker in zip(stocks_dates, STOCK_TICKERS):
        with ThreadPoolExecutor() as exe:
            stocks_futures.append([exe.submit(fetch_data, date, stock_ticker) for date in stock_dates['date']])

    for stock_futures, destination_file in zip(stocks_futures, DESTINATION_FILES):
        stock_data = prepare_stock_data_df(stock_futures)
        write_to_csv(stock_data, destination_file)


if __name__ == '__main__':
    main()
