import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, Future

from constants import BTC_TICKER, DESTINATION_FILE, SOURCE_FILE


def prepare_data_frame(futures: list[Future]) -> pd.DataFrame:
    df = pd.concat([future.result() for future in futures])

    return df.reset_index()


def clean_up_df(data_frame: pd.DataFrame) -> pd.DataFrame:
    data_frame['date'] = data_frame['raw_line'].str.split().str[0]
    data_frame['date'] = pd.to_datetime(data_frame['date'], format="%Y-%m-%d")

    return data_frame[['date']].drop_duplicates().sort_values(by='date').reset_index(drop=True)


def get_dates(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, header=None, names=['raw_line'])
    clean_df = clean_up_df(df)

    return clean_df


def get_next_date(date: datetime) -> datetime:
    return date + timedelta(days=1)


def fetch_data(date: datetime) -> None:
    return BTC_TICKER.history(start=date, end=get_next_date(date))


def add_percentage(data_frame: pd.DataFrame) -> None:
    data_frame["percent_change"] = data_frame["Close"].pct_change() * 100
    data_frame["percent_change"] = data_frame["percent_change"].fillna(0)


def write_to_csv(stock_data: pd.DataFrame) -> None:
    add_percentage(stock_data)

    stock_data["stock_type"] = "BTC"
    stock_data[["Date", "stock_type", "percent_change"]].to_csv(DESTINATION_FILE)


def main() -> None:
    dates = get_dates(SOURCE_FILE)

    with ThreadPoolExecutor() as exe:
        futures = [exe.submit(fetch_data, date) for date in dates['date']]

    btc_data = prepare_data_frame(futures)
    
    write_to_csv(btc_data)


if __name__ == '__main__':
    main()
