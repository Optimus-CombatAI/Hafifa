"""Plan Yahoo windows, fetch them concurrently, merge bars, write one CSV per ticker."""

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import pandas as pd

from core.constant import FETCH_BATCH_SIZE, FETCH_PADDING
from domain.client import YahooFetchError, get_stock_history
from domain.models import Stock, StockTicker, empty_ohlcv_frame

logger = logging.getLogger(__name__)

FetchHistory = Callable[[StockTicker, datetime, datetime], pd.DataFrame]


def plan_windows(
    hours: pd.DatetimeIndex, batch_size: int = FETCH_BATCH_SIZE
) -> list[tuple[datetime, datetime]]:
    stamps = list(hours.floor("h").drop_duplicates().sort_values())
    windows: list[tuple[datetime, datetime]] = []
    for start in range(0, len(stamps), batch_size):
        batch = stamps[start : start + batch_size]
        windows.append((batch[0] - FETCH_PADDING, batch[-1] + FETCH_PADDING))
    return windows


def merge_ohlcv(*frames: pd.DataFrame) -> pd.DataFrame:
    parts = [frame for frame in frames if not frame.empty]
    if not parts:
        return empty_ohlcv_frame()
    combined = pd.concat(parts).sort_index()
    return combined.loc[~combined.index.duplicated(keep="last"), :]


def run_pipeline(
    stocks: list[Stock],
    output_dir: Path,
    *,
    max_workers: int,
    fetch: FetchHistory = get_stock_history,
) -> list[Stock]:
    output_dir.mkdir(parents=True, exist_ok=True)
    jobs = [
        (stock.ticker, start, end)
        for stock in stocks
        for start, end in plan_windows(stock.hours)
    ]
    logger.info("Fetching %d window(s) on up to %d thread(s)", len(jobs), max_workers)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(lambda job: (job[0], fetch(*job)), jobs))

    frames: dict[StockTicker, list[pd.DataFrame]] = {stock.ticker: [] for stock in stocks}
    for ticker, frame in results:
        frames[ticker].append(frame)

    fetched: list[Stock] = []
    for stock in stocks:
        data = merge_ohlcv(*frames[stock.ticker])
        if len(stock.hours) and data.empty:
            logger.error("No bars merged for %s after fetch", stock.ticker.value)
            raise YahooFetchError(f"No bars fetched for {stock.ticker.value}")
        data.to_csv(output_dir / f"{stock.ticker.value}.csv", index_label="time")
        fetched.append(Stock(stock.ticker, stock.hours, data))
        logger.info("Wrote %s (%d bars)", stock.ticker.value, len(data))
    return fetched
