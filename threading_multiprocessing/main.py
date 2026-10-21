"""CLI: load hour files, fetch each stock on its own thread, write the CSV."""

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from constants import COLUMNS, PACKAGE_DIR, STOCKS
from logging_config import configure_logging
from stock_prices import process_stock

logger = logging.getLogger(__name__)


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PACKAGE_DIR / path


def load_hours(path: Path) -> list[str]:
    if not path.is_file():
        raise OSError(f"Hour file not found: {path}")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    load_dotenv(PACKAGE_DIR / ".env")
    configure_logging()

    destination = os.environ.get("DESTINATION_FILE")
    if not destination:
        raise SystemExit("Missing environment variable: DESTINATION_FILE")

    tasks = []
    for name, ticker, dates_env in STOCKS:
        dates_path = os.environ.get(dates_env)
        if dates_path:
            path = resolve_path(dates_path)
            hours = load_hours(path)
            tasks.append((name, ticker, hours))
            logger.info("Loaded %d hours for %s from %s", len(hours), name, path)

    if not tasks:
        needed = ", ".join(env for _, _, env in STOCKS)
        raise SystemExit(f"No hour files configured. Set one or more of: {needed}")

    logger.info("Fetching %d stock(s) with ThreadPoolExecutor", len(tasks))
    names, tickers, hours_lists = zip(*tasks)
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        parts = list(executor.map(process_stock, names, tickers, hours_lists))

    frame = pd.concat(parts, ignore_index=True)
    if not frame.empty:
        frame = frame.sort_values(["stock type", "hour"], kind="stable")

    output_path = resolve_path(destination)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False, columns=list(COLUMNS))

    logger.info("Wrote %s (%d rows, %d stocks)", output_path, len(frame), len(tasks))
    if frame.empty:
        logger.warning(
            "No rows written; Yahoo 1h history is usually limited to ~730 days."
        )


if __name__ == "__main__":
    main()
