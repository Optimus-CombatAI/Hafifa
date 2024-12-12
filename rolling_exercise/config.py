import pydantic


class Settings(pydantic.BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost/air_quality_db"

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "air_quality_api_logger.log"

    class Config:
        env_file = ".env"


settings = Settings()
