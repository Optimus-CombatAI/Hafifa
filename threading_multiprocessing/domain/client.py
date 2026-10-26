"""Yahoo Finance client for hourly stock history."""

import logging
from datetime import datetime

import pandas as pd
import yfinance as yf

from domain.models import StockTicker, as_ohlcv_frame

logger = logging.getLogger(__name__)


class YahooFetchError(RuntimeError):
    """Yahoo download failed or returned no data for a window."""


def get_stock_history(
    ticker: StockTicker,
    start: datetime,
    end: datetime,
    interval: str = "1h",
) -> pd.DataFrame:
    """Download OHLCV bars for one window; raises YahooFetchError on failure or empty data."""
    try:
        history = yf.download(
            ticker.value,
            start=start,
            end=end,
            interval=interval,
            progress=False,
            auto_adjust=False,
        )
    except Exception as exc:
        logger.exception(
            "Yahoo download failed for %s (%s to %s)",
            ticker.value,
            start,
            end,
        )
        raise YahooFetchError(
            f"Yahoo download failed for {ticker.value} ({start} to {end})"
        ) from exc

    if history is None or history.empty:
        logger.error(
            "Empty Yahoo response for %s (%s to %s)",
            ticker.value,
            start,
            end,
        )
        raise YahooFetchError(
            f"Empty Yahoo response for {ticker.value} ({start} to {end})"
        )
    return as_ohlcv_frame(history)
