"""Application logging setup."""

import logging
import os

from constants import LOG_DATE_FORMAT, LOG_FORMAT


def configure_logging() -> None:
    """Configure stderr logging once; honor ``LOG_LEVEL`` from the environment."""
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, None)
    if not isinstance(level, int):
        level = logging.INFO

    logging.basicConfig(level=level, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)
