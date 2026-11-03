import logging
from pathlib import Path


def configure_logging(log_file_path: Path):
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[logging.FileHandler(log_file_path, encoding="utf-8"), logging.StreamHandler()],
    )
