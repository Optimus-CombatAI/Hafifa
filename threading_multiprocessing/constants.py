from pathlib import Path

import pandas as pd

PACKAGE_DIR = Path(__file__).resolve().parent
FETCH_PADDING = pd.Timedelta(days=2)

STOCKS = (
    ("Bitcoin", "BTC-USD", "BITCOIN_DATES"),
    ("Google", "GOOGL", "GOOGLE_DATES"),
    ("Amazon", "AMZN", "AMAZON_DATES"),
)

COLUMNS = ("hour", "stock type", "percentage change")

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
