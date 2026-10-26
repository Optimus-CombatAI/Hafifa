"""Read the requested-hours files into Stock objects."""

from collections.abc import Iterable, Mapping
from pathlib import Path

import pandas as pd

from core.config import Config
from core.constant import RAW_DATA_DIR
from domain.models import Stock, StockTicker


def load_stocks(
    tickers: Iterable[StockTicker] = tuple(StockTicker),
    *,
    config: Config | None = None,
    hours_dir: Path | None = None,
    hours_files: Mapping[StockTicker, Path] | None = None,
) -> list[Stock]:
    """One timestamp per line; blank or unparsable lines are skipped.

    ``config`` supplies ``hours_dir`` and any ``*_dates`` overrides.
    """
    tickers = tuple(tickers)
    hours_dir = hours_dir or (config.hours_dir if config else RAW_DATA_DIR)
    files = dict(hours_files or {})
    if config:
        for ticker in tickers:
            override = getattr(config, f"{ticker.name.lower()}_dates", None)
            if override:
                files[ticker] = override

    stocks: list[Stock] = []
    for ticker in tickers:
        path = files.get(ticker) or hours_dir / f"{ticker.value}.txt"
        lines = [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        hours = pd.to_datetime(lines, format="ISO8601", errors="coerce")
        stocks.append(Stock(ticker, hours.dropna().sort_values()))
    return stocks
