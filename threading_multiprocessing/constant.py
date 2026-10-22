"""Tracked stocks, CSV layout, and logging formats."""

from pathlib import Path

import pandas as pd

from models import Stock

PACKAGE_DIR = Path(__file__).resolve().parent
FETCH_PADDING = pd.Timedelta(days=2)

STOCKS = (
    Stock(name="Bitcoin", ticker="BTC-USD", dates_env="BITCOIN_DATES"),
    Stock(name="Google", ticker="GOOGL", dates_env="GOOGLE_DATES"),
    Stock(name="Amazon", ticker="AMZN", dates_env="AMAZON_DATES"),
)

COLUMNS = ("hour", "stock type", "percentage change")

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
