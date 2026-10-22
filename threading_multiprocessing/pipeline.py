"""Multithreaded fetch, merge, and CSV export."""

import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from constant import COLUMNS
from models import StockTask
from stock_prices import empty_result, process_stock

logger = logging.getLogger(__name__)


def fetch_all(tasks: list[StockTask]) -> list[pd.DataFrame]:
    logger.info("Fetching %d stock(s) with ThreadPoolExecutor", len(tasks))
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        return list(executor.map(process_stock, tasks))


def combine_frames(parts: list[pd.DataFrame]) -> pd.DataFrame:
    non_empty = [part for part in parts if not part.empty]
    if not non_empty:
        return empty_result()
    frame = pd.concat(non_empty, ignore_index=True)
    return frame.sort_values(["stock type", "hour"], kind="stable", ignore_index=True)


def write_report(frame: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False, columns=list(COLUMNS))

    logger.info("Wrote %s (%d rows)", output_path, len(frame))
    if frame.empty:
        logger.warning("No rows written; Yahoo 1h history is usually limited to ~730 days.")
