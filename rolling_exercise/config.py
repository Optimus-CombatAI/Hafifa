import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    DATABASE_URL: str = "sqlite:///./air_quality.db"

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "air_quality_api_logger.log"

    class Config:
        env_file = ".env"


settings = Settings()
