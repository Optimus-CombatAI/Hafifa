"""Application logging setup."""

import logging
import os

from constant import LOG_DATE_FORMAT, LOG_FORMAT


def configure_logging() -> None:
    """Configure stderr logging; honor ``LOG_LEVEL`` from the environment."""
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    logging.getLogger("yfinance").setLevel(logging.ERROR)
