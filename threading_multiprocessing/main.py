"""Load hour files, fetch each stock on its own thread, write the CSV."""

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

DIR = Path(__file__).resolve().parent
FETCH_PADDING = pd.Timedelta(days=2)
STOCKS = (
    ("Bitcoin", "BTC-USD", "BITCOIN_DATES"),
    ("Google", "GOOGL", "GOOGLE_DATES"),
    ("Amazon", "AMZN", "AMAZON_DATES"),
)
COLUMNS = ("hour", "stock type", "percentage change")


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else DIR / path


def load_hours(path: Path) -> list[str]:
    if not path.is_file():
        raise OSError(f"Hour file not found: {path}")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def hourly_closes(hist: pd.DataFrame) -> pd.Series:
    """Last close per UTC hour."""
    if hist.empty:
        return pd.Series(dtype=float)

    index = hist.index
    if index.tz is not None:
        index = index.tz_convert("UTC").tz_localize(None)

    closes = hist["Close"].copy()
    closes.index = index.floor("h")
    return closes.groupby(closes.index).last()


def percentage_changes(
    closes: pd.Series, raw_hours: list[str], stock_type: str
) -> pd.DataFrame:
    """Hour-over-hour % change for requested timestamps (vectorized lookups).

    Uses calendar ``t`` and ``t - 1h`` labels, not ``Series.shift()``, so gaps
    in Yahoo's hourly index do not pair the wrong bars.
    """
    requested = pd.DataFrame({"hour": raw_hours})
    requested["bar"] = pd.to_datetime(requested["hour"], errors="coerce").dt.floor("h")
    requested = requested.dropna(subset=["bar"])
    if requested.empty:
        return pd.DataFrame(columns=list(COLUMNS))

    requested["prev_bar"] = requested["bar"] - pd.Timedelta(hours=1)
    requested["curr_close"] = requested["bar"].map(closes)
    requested["prev_close"] = requested["prev_bar"].map(closes)

    ok = (
        requested["curr_close"].notna()
        & requested["prev_close"].notna()
        & (requested["prev_close"] != 0)
    )
    pct = (requested.loc[ok, "curr_close"] / requested.loc[ok, "prev_close"] - 1) * 100

    return pd.DataFrame(
        {
            "hour": requested.loc[ok, "hour"].to_numpy(),
            "stock type": stock_type,
            "percentage change": pct.to_numpy(),
        }
    )


def process_stock(stock_type: str, ticker: str, hours: list[str]) -> pd.DataFrame:
    """One Yahoo fetch for the span of ``hours``, then vectorized % changes."""
    if not hours:
        return pd.DataFrame(columns=list(COLUMNS))

    bars = pd.to_datetime(hours, errors="coerce").floor("h")
    valid_bars = bars.dropna()
    if valid_bars.empty:
        return pd.DataFrame(columns=list(COLUMNS))

    start = (valid_bars.min() - FETCH_PADDING).strftime("%Y-%m-%d")
    # Extra day: Yahoo ``end`` is exclusive when passed as a date.
    end = (valid_bars.max() + FETCH_PADDING + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    hist = yf.Ticker(ticker).history(start=start, end=end, interval="1h")
    closes = hourly_closes(hist)
    if closes.empty:
        return pd.DataFrame(columns=list(COLUMNS))

    return percentage_changes(closes, hours, stock_type)


def main() -> None:
    load_dotenv(DIR / ".env")
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)

    destination = os.environ.get("DESTINATION_FILE")
    if not destination:
        raise SystemExit("Missing environment variable: DESTINATION_FILE")

    tasks = []
    for name, ticker, dates_env in STOCKS:
        dates_path = os.environ.get(dates_env)
        if dates_path:
            tasks.append((name, ticker, load_hours(resolve_path(dates_path))))

    if not tasks:
        needed = ", ".join(env for _, _, env in STOCKS)
        raise SystemExit(f"No hour files configured. Set one or more of: {needed}")

    names, tickers, hours_lists = zip(*tasks)
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        parts = list(executor.map(process_stock, names, tickers, hours_lists))

    frame = pd.concat(parts, ignore_index=True)
    if not frame.empty:
        frame = frame.sort_values(["stock type", "hour"], kind="stable")

    output_path = resolve_path(destination)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False, columns=list(COLUMNS))

    print(f"Wrote {output_path} ({len(frame)} rows, {len(tasks)} stocks)")
    if frame.empty:
        print("No rows written; Yahoo 1h history is usually limited to ~730 days.")


if __name__ == "__main__":
    main()
