"""Yahoo hourly history and hour-over-hour percentage change."""

import pandas as pd
import yfinance as yf

from constants import COLUMNS, FETCH_PADDING


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
