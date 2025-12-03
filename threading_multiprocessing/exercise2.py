from typing import Dict, Any, Optional, List, Tuple
import os
import pandas as pd
import yfinance as yf
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, Future


STOCKS: Dict[str, Dict[str, str]] = {
    "Bitcoin": {
        "env_var": "BITCOIN_DATES",
        "ticker": "BTC-USD"
    },
    "Google": {
        "env_var": "GOOGLE_DATES",
        "ticker": "GOOG"
    },
    "Amazon": {
        "env_var": "AMAZON_DATES",
        "ticker": "AMZN"
    }
}


logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")
logger: logging.Logger = logging.getLogger(__name__)


def load_dates_from_env(env_var: str) -> pd.DataFrame:
    path: str = os.environ[env_var]
    df: pd.DataFrame = pd.read_csv(path, header=None, names=["hour"])
    df = df.dropna()
    df["hour"] = df["hour"].astype(str)

    return df


def get_price_for_date(ticker: str, date_string: str) -> Optional[float]:
    # Try full timestamp with microseconds
    try:
        dt_start: datetime = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        # Fallback: timestamp without microseconds
        dt_start = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

    dt_end: datetime = dt_start + timedelta(minutes=1)
    ans = yf.Ticker(ticker)
    data = ans.history(start=dt_start, end=dt_end)

    if data.empty:
        return None

    price: float = float(data["Close"].iloc[0])
    return price


def worker(ticker: str, dates_df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    for date in dates_df["hour"]:
        price: Optional[float] = get_price_for_date(ticker, date)

        if price is None:
            logger.warning(f"{ticker} : no price for {date}")
        else:
            rows.append({
                "ticker": ticker,
                "hour": date,
                "price": price
            })

    return pd.DataFrame(rows)


def main() -> pd.DataFrame:
    all_results: Dict[str, pd.DataFrame] = {}

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures: List[Tuple[str, Future]] = []

        for stock_name, info in STOCKS.items():
            env_var_name: str = info["env_var"]
            dates: pd.DataFrame = load_dates_from_env(env_var_name)

            future: Future = executor.submit(worker, info["ticker"], dates, logger)
            futures.append((stock_name, future))

        for stock_name, future in futures:
            result: pd.DataFrame = future.result()
            all_results[stock_name] = result

    final_df: pd.DataFrame = pd.concat(all_results.values(), ignore_index=True)
    logger.info("All results successfully combined.")
    final_df.to_csv("results.csv", index=False)

    return final_df


if __name__ == "__main__":
    main()
