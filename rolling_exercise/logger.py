import logging
from typing import Optional


class LoggerConfig:
    def __init__(self, log_file: str = "app.log", level: int = logging.INFO,
                 fmt: str = "%(asctime)s [%(levelname)s] %(message)s") -> None:
        self.log_file = log_file
        self.level = level
        self.formatter = logging.Formatter(fmt)

        self._configure_root()
        self._configure_app_logger()
        self._configure_sqlalchemy_logger()

    def _configure_root(self) -> None:
        root = logging.getLogger()
        root.setLevel(self.level)

        if not root.handlers:
            handler = logging.FileHandler(self.log_file, mode="a")
            handler.setLevel(self.level)
            handler.setFormatter(self.formatter)
            root.addHandler(handler)

    def _configure_app_logger(self) -> None:
        self.app_logger = logging.getLogger("app")
        self.app_logger.setLevel(self.level)
        self.app_logger.propagate = True

    def _configure_sqlalchemy_logger(self) -> None:
        sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
        sqlalchemy_logger.setLevel(self.level)
        sqlalchemy_logger.propagate = True

    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        return logging.getLogger(name) if name else self.app_logger
