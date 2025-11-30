import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, Future

from constants import BTC_TICKER, DESTINATION_FILE, SOURCE_FILE


def prepare_stock_data_df(futures: list[Future]) -> pd.DataFrame:
    combined = pd.concat([future.result() for future in futures])

    return combined.reset_index()


def clean_up_dates(dates_df: pd.DataFrame) -> pd.DataFrame:
    dates_df['date'] = pd.to_datetime(dates_df['raw_line'], format="%Y-%m-%d %H:%M:%S.%f")
    dates_df['date'] = dates_df['date'].dt.normalize()

    return dates_df[['date']].drop_duplicates().sort_values(by='date').reset_index(drop=True)


def get_dates(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, header=None, names=['raw_line'])
    clean_df = clean_up_dates(df)

    return clean_df


def get_next_date(date: datetime) -> datetime:
    return date + timedelta(days=1)


def fetch_data(date: datetime) -> None:
    return BTC_TICKER.history(start=date, end=get_next_date(date))


def add_percentage(dates_df: pd.DataFrame) -> None:
    dates_df["percent_change"] = dates_df["Close"].pct_change() * 100
    dates_df["percent_change"] = dates_df["percent_change"].fillna(0)


def write_to_csv(stock_data: pd.DataFrame) -> None:
    add_percentage(stock_data)

    stock_data["stock_type"] = "BTC"
    stock_data[["Date", "stock_type", "percent_change"]].to_csv(DESTINATION_FILE)


def main() -> None:
    dates = get_dates(SOURCE_FILE)

    with ThreadPoolExecutor() as exe:
        futures = [exe.submit(fetch_data, date) for date in dates['date']]

    btc_data = prepare_stock_data_df(futures)

    write_to_csv(btc_data)


if __name__ == '__main__':
    main()
