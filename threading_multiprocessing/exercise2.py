import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor, Future

import pandas as pd
import yfinance as yf
from config import STOCKS, logger

# -------------------------
# Load dates from env file
# -------------------------
def load_dates_from_env(dates_env_var: str) -> pd.DataFrame:
    """
    Load timestamps from a file specified in an environment variable.
    """
    path: str = os.environ[dates_env_var]
    df: pd.DataFrame = pd.read_csv(path, header=None, names=["hour"])
    df["hour"] = df["hour"].astype(str)
    return df


# -------------------------
# Fetch price for one timestamp
# -------------------------
def get_price_for_date(ticker: str, date_string: str) -> Optional[float]:
    """
    Fetch the closing price for a given ticker and timestamp.
    Handles timestamps with or without microseconds.
    """
    try:
        dt_start: datetime = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        dt_start = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

    dt_end: datetime = dt_start + timedelta(minutes=1)

    data = yf.Ticker(ticker).history(start=dt_start, end=dt_end)
    if data.empty:
        return None

    return float(data["Close"].iloc[0])


# -------------------------
# Fetch all prices for one ticker
# -------------------------
def fetch_prices_for_ticker(ticker: str, dates_df: pd.DataFrame) -> pd.DataFrame:
    """
    Fetch prices for a specific ticker for all given timestamps.
    """
    rows: List[Dict[str, Any]] = []

    for date in dates_df["hour"]:
        price: Optional[float] = get_price_for_date(ticker, date)

        if price is None:
            logger.warning(f"{ticker} : no price for {date}")
        else:
            rows.append({"ticker": ticker, "hour": date, "price": price})

    return pd.DataFrame(rows)


# -------------------------
# Submit tasks to threads
# -------------------------
def submit_tasks(executor: ThreadPoolExecutor) -> Dict[str, Future]:
    """
    Submit one task per ticker to the executor and return a dict of futures.
    """
    futures: Dict[str, Future] = {}

    for stock_name, info in STOCKS.items():
        dates_df = load_dates_from_env(info["dates_env_var"])
        future = executor.submit(fetch_prices_for_ticker, info["ticker"], dates_df)
        futures[stock_name] = future

    return futures


# -------------------------
# Collect results from futures
# -------------------------
def collect_results(futures: Dict[str, Future]) -> Dict[str, pd.DataFrame]:
    """
    Wait for all futures and collect the DataFrames.
    """
    results: Dict[str, pd.DataFrame] = {}

    for stock_name, future in futures.items():
        results[stock_name] = future.result()

    return results


# -------------------------
# Build final DataFrame (merge + pct change)
# -------------------------
def build_final_dataframe(results: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Merge all DataFrames and compute percentage change per ticker.
    """
    final_df: pd.DataFrame = pd.concat(results.values(), ignore_index=True)

    # Sort before calculating percentage change
    final_df.sort_values(by=["ticker", "hour"], inplace=True)

    # Add percentage change column
    final_df["pct_change"] = final_df.groupby("ticker")["price"].pct_change()

    return final_df


# -------------------------
# Main
# -------------------------
def main() -> pd.DataFrame:
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = submit_tasks(executor)
        results = collect_results(futures)

    final_df = build_final_dataframe(results)

    logger.info("All results successfully combined.")
    final_df.to_csv("results.csv", index=False)

    return final_df


if __name__ == "__main__":
    main()