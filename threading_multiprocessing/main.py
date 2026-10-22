"""CLI entry: bootstrap, load config, run pipeline."""

import logging

from dotenv import load_dotenv

from config import ConfigError, load_stock_tasks, require_destination
from constant import PACKAGE_DIR
from logging_config import configure_logging
from pipeline import combine_frames, fetch_all, write_report

logger = logging.getLogger(__name__)


def main() -> None:
    load_dotenv(PACKAGE_DIR / ".env")
    configure_logging()

    try:
        destination = require_destination()
        tasks = load_stock_tasks()
        logger.info("Running pipeline for %d stock task(s)", len(tasks))
        frame = combine_frames(fetch_all(tasks))
        write_report(frame, destination)
        logger.info("Pipeline finished")
    except ConfigError as error:
        logger.error("Configuration error: %s", error)
        raise SystemExit(f"Configuration error: {error}") from None
    except Exception:
        logger.exception("Pipeline failed")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
