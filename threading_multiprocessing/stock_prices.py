"""Yahoo hourly history and hour-over-hour percentage change."""

import logging
from collections.abc import Sequence

import pandas as pd
import yfinance as yf

from constant import COLUMNS, FETCH_PADDING
from models import StockTask

logger = logging.getLogger(__name__)


def empty_result() -> pd.DataFrame:
    return pd.DataFrame(columns=list(COLUMNS))


def parse_hours(raw_hours: Sequence[str]) -> pd.DataFrame:
    """Raw ``hour`` strings with their floored ``bar``; unparsable lines are dropped."""
    requested = pd.DataFrame({"hour": list(raw_hours)})
    requested["bar"] = pd.to_datetime(requested["hour"], errors="coerce").dt.floor("h")
    return requested.dropna(subset=["bar"])


def hourly_closes(history: pd.DataFrame) -> pd.Series:
    """Last close per UTC hour."""
    if history.empty:
        return pd.Series(dtype=float)

    index = history.index
    if index.tz is not None:
        index = index.tz_convert("UTC").tz_localize(None)
    return history["Close"].groupby(index.floor("h")).last()


def fetch_hourly_closes(ticker: str, bars: pd.Series) -> pd.Series:
    """One Yahoo request covering every bar in ``bars``, padded on both sides."""
    start = (bars.min() - FETCH_PADDING).strftime("%Y-%m-%d")
    # Yahoo's ``end`` is exclusive when passed as a date.
    end = (bars.max() + FETCH_PADDING + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    logger.debug("%s: fetching 1h history %s to %s", ticker, start, end)
    history = yf.Ticker(ticker).history(start=start, end=end, interval="1h")
    return hourly_closes(history)


def percentage_changes(
    closes: pd.Series, requested: pd.DataFrame, stock_type: str
) -> pd.DataFrame:
    """Hour-over-hour % change for each requested bar.

    Uses calendar ``t`` and ``t - 1h`` labels, not ``Series.shift()``, so gaps
    in Yahoo's hourly index do not pair the wrong bars.
    """
    current = requested["bar"].map(closes)
    previous = (requested["bar"] - pd.Timedelta(hours=1)).map(closes)
    ok = current.notna() & previous.notna() & (previous != 0)

    return pd.DataFrame(
        {
            "hour": requested.loc[ok, "hour"].to_numpy(),
            "stock type": stock_type,
            "percentage change": ((current[ok] / previous[ok] - 1) * 100).to_numpy(),
        }
    )


def process_stock(task: StockTask) -> pd.DataFrame:
    """Fetch one stock's history and compute % changes for its requested hours."""
    requested = parse_hours(task.hours)
    skipped = len(task.hours) - len(requested)
    if skipped:
        logger.debug("%s: skipped %d unparsable hour lines", task.label, skipped)
    if requested.empty:
        logger.warning("%s: no valid timestamps in hour file", task.label)
        return empty_result()

    try:
        closes = fetch_hourly_closes(task.stock.ticker, requested["bar"])
    except Exception:
        logger.exception("%s: Yahoo fetch failed", task.label)
        return empty_result()
    if closes.empty:
        logger.warning("%s: Yahoo returned no hourly closes", task.label)
        return empty_result()

    frame = percentage_changes(closes, requested, task.stock.name)
    if frame.empty:
        logger.warning("%s: no requested hour had a previous-hour close", task.label)
    else:
        logger.info(
            "%s: %d rows from %d requested hours", task.label, len(frame), len(task.hours)
        )
    return frame
