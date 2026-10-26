from datetime import timedelta
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PACKAGE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = PACKAGE_DIR / "data" / "processed"
ENV_FILE = PACKAGE_DIR / ".env"

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_DESTINATION_FILE = Path("stock_changes.csv")
DEFAULT_MAX_WORKERS = 8

OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")

# Yahoo range padding around each batch of requested hours.
FETCH_PADDING = timedelta(days=2)
# How many requested hours to group into one fetch window.
FETCH_BATCH_SIZE = 100
