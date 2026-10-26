"""CLI entry: fetch hourly bars, write per-ticker CSVs, then the destination report."""

import logging
import warnings

from core.config import Config
from core.constant import LOG_DATE_FORMAT, LOG_FORMAT
from domain.load import load_stocks
from domain.pipeline import run_pipeline
from domain.report import write_destination_csv

logger = logging.getLogger(__name__)


def main() -> None:
    config = Config()
    logging.basicConfig(
        level=config.log_level,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        force=True,
    )
    logging.getLogger("yfinance").setLevel(logging.ERROR)
    try:
        from pandas.errors import Pandas4Warning
    except ImportError:
        pass
    else:
        warnings.filterwarnings("ignore", category=Pandas4Warning, module="yfinance")

    try:
        stocks = run_pipeline(
            load_stocks(config=config),
            config.output_dir,
            max_workers=config.max_workers,
        )
        changes = write_destination_csv(stocks, config.destination_file)
    except Exception:
        logger.exception("Pipeline failed")
        raise SystemExit(1) from None

    for stock in stocks:
        logger.info("%s: %d hourly bar(s)", stock.name, len(stock.data))
    logger.info("Wrote %d ticker CSV file(s) to %s", len(stocks), config.output_dir)
    logger.info("Wrote destination report (%d row(s)) → %s", len(changes), config.destination_file)


if __name__ == "__main__":
    main()
