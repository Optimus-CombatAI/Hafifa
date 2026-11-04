from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True, env_file=".env")

    log_file_path: Path
    database_url: str
    api_host: str
    api_port: int = Field(gt=0)
