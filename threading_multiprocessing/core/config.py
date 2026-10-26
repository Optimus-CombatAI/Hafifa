from pathlib import Path
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.constant import (
    DEFAULT_DESTINATION_FILE,
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAX_WORKERS,
    ENV_FILE,
    PACKAGE_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
)


class Config(BaseSettings):
    """Environment / ``.env``: LOG_LEVEL, OUTPUT_DIR, MAX_WORKERS, DESTINATION_FILE, *_DATES."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = DEFAULT_LOG_LEVEL
    output_dir: Path = PROCESSED_DATA_DIR
    destination_file: Path = DEFAULT_DESTINATION_FILE
    max_workers: int = Field(default=DEFAULT_MAX_WORKERS, gt=0)
    hours_dir: Path = RAW_DATA_DIR

    bitcoin_dates: Path | None = None
    google_dates: Path | None = None
    amazon_dates: Path | None = None

    @field_validator("output_dir", "hours_dir")
    @classmethod
    def _relative_to_package(cls, path: Path) -> Path:
        return path if path.is_absolute() else PACKAGE_DIR / path

    @field_validator("bitcoin_dates", "google_dates", "amazon_dates")
    @classmethod
    def _optional_relative_to_package(cls, path: Path | None) -> Path | None:
        if path is None:
            return None
        return path if path.is_absolute() else PACKAGE_DIR / path

    @model_validator(mode="after")
    def _resolve_destination_file(self) -> Self:
        destination = self.destination_file
        if destination.is_absolute():
            return self
        if len(destination.parts) == 1:
            self.destination_file = self.output_dir / destination.name
        else:
            self.destination_file = PACKAGE_DIR / destination
        return self
