"""Tickers, OHLCV frames, and loaded stock state."""

from dataclasses import dataclass, field
from enum import StrEnum

import pandas as pd

from core.constant import OHLCV_COLUMNS


class StockTicker(StrEnum):
    """Yahoo Finance symbols for the exercise stocks."""

    BITCOIN = "BTC-USD"
    GOOGLE = "GOOGL"
    AMAZON = "AMZN"

    @property
    def display_name(self) -> str:
        return self.name.title()


def empty_ohlcv_frame() -> pd.DataFrame:
    return pd.DataFrame(
        columns=list(OHLCV_COLUMNS),
        index=pd.DatetimeIndex([], name="time"),
    )


def as_ohlcv_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if isinstance(frame.columns, pd.MultiIndex):
        frame = frame.copy()
        frame.columns = frame.columns.get_level_values(0)
    frame = frame.loc[:, list(OHLCV_COLUMNS)]
    index = pd.DatetimeIndex(frame.index)
    if index.tz is not None:
        index = index.tz_convert("UTC").tz_localize(None)
    frame.index = index
    frame.index.name = "time"
    return frame.sort_index()


@dataclass
class Stock:
    ticker: StockTicker
    hours: pd.DatetimeIndex
    data: pd.DataFrame = field(default_factory=empty_ohlcv_frame)

    @property
    def name(self) -> str:
        return self.ticker.display_name
