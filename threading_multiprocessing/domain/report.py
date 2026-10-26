"""Build the exercise destination CSV: hour, stock type, percentage change."""

from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from domain.models import Stock

COLUMNS = ("hour", "stock type", "percentage change")


def build_changes_table(stocks: Sequence[Stock]) -> pd.DataFrame:
    """One row per requested hour where an hourly bar and prior close exist."""
    rows: list[dict[str, object]] = []
    for stock in stocks:
        for requested_hour in stock.hours:
            change = hourly_percentage_change(stock.data, requested_hour)
            if change is None:
                continue
            rows.append(
                {
                    "hour": format_requested_hour(requested_hour),
                    "stock type": stock.name,
                    "percentage change": change,
                }
            )
    frame = pd.DataFrame(rows, columns=list(COLUMNS))
    if frame.empty:
        return frame
    return frame.sort_values(["hour", "stock type"], kind="mergesort").reset_index(drop=True)


def write_destination_csv(stocks: Sequence[Stock], path: Path) -> pd.DataFrame:
    path.parent.mkdir(parents=True, exist_ok=True)
    table = build_changes_table(stocks)
    table.to_csv(path, index=False)
    return table


def hourly_percentage_change(
    bars: pd.DataFrame, requested_hour: pd.Timestamp
) -> float | None:
    """Percent change from the previous hourly close to the close at the matched bar."""
    if bars.empty:
        return None
    bar_time = _bar_for_requested_hour(pd.DatetimeIndex(bars.index), requested_hour)
    if bar_time is None:
        return None
    position = bars.index.get_loc(bar_time)
    if not isinstance(position, int) or position == 0:
        return None
    previous_close = float(bars.iloc[position - 1]["Close"])
    if previous_close == 0:
        return None
    current_close = float(bars.iloc[position]["Close"])
    return (current_close - previous_close) / previous_close * 100


def _bar_for_requested_hour(
    bar_times: pd.DatetimeIndex, requested_hour: pd.Timestamp
) -> pd.Timestamp | None:
    """Use the first hourly bar at or after the requested timestamp, floored to the hour."""
    position = bar_times.searchsorted(requested_hour.floor("h").to_datetime64(), side="left")
    if position >= len(bar_times):
        return None
    found = bar_times[position]
    return found if isinstance(found, pd.Timestamp) else None


def format_requested_hour(timestamp: pd.Timestamp) -> str:
    """Match the timestamp strings in the raw hours files (microseconds, no timezone)."""
    return f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}.{timestamp.microsecond:06d}"
