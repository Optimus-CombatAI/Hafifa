# config.py
from typing import Dict
import logging

# ---- STOCKS CONFIG ----
STOCKS: Dict[str, Dict[str, str]] = {
    "Bitcoin": {
        "dates_env_var": "BITCOIN_DATES",
        "ticker": "BTC-USD"
    },
    "Google": {
        "dates_env_var": "GOOGLE_DATES",
        "ticker": "GOOG"
    },
    "Amazon": {
        "dates_env_var": "AMAZON_DATES",
        "ticker": "AMZN"
    }
}

# ---- LOGGER CONFIG ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("stock_logger")
