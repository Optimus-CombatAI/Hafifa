"""Environment variables, paths, and hour-file loading."""

import logging
import os
from pathlib import Path

from constant import PACKAGE_DIR, STOCKS
from models import StockTask

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Required configuration is missing or invalid."""


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PACKAGE_DIR / path


def load_hours(path: Path) -> tuple[str, ...]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return tuple(line.strip() for line in lines if line.strip())


def require_destination() -> Path:
    destination = os.environ.get("DESTINATION_FILE")
    if not destination:
        raise ConfigError("Missing environment variable: DESTINATION_FILE")
    return resolve_path(destination)


def load_stock_tasks() -> list[StockTask]:
    tasks: list[StockTask] = []
    for stock in STOCKS:
        dates_path = os.environ.get(stock.dates_env)
        if not dates_path:
            continue

        path = resolve_path(dates_path)
        try:
            hours = load_hours(path)
        except FileNotFoundError:
            raise ConfigError(f"{stock.dates_env}: hour file not found: {path}") from None
        tasks.append(StockTask(stock=stock, hours=hours))
        logger.info("Loaded %d hours for %s from %s", len(hours), stock.name, path)

    if not tasks:
        needed = ", ".join(stock.dates_env for stock in STOCKS)
        raise ConfigError(f"No hour files configured. Set one or more of: {needed}")

    return tasks
