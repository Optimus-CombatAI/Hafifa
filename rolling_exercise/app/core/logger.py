import logging

LOGGER_NAME = "air_quality"


def setup_logging(level: int = logging.INFO) -> None:
    logger = logging.getLogger(LOGGER_NAME)

    if logger.handlers:
        return

    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    logger.propagate = False
