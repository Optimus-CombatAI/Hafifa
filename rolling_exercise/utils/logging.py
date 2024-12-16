import logging
from rolling_exercise.config import settings


def setup_logger():
    logger = logging.getLogger("air_quality_api_logger")
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setLevel(log_level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


air_quality_api_logger = setup_logger()
