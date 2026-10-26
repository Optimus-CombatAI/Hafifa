from collections.abc import Sequence

import pandas as pd

from core.constant import OHLCV_COLUMNS


def ohlcv_bars(*timestamps: str, close: float | Sequence[float] = 1.0) -> pd.DataFrame:
    prices = [float(close)] * len(timestamps) if isinstance(close, (int, float)) else [float(p) for p in close]
    return pd.DataFrame(
        {column: prices for column in OHLCV_COLUMNS},
        index=pd.DatetimeIndex(timestamps, name="time"),
    )
