from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATE_FORMAT: str = "%Y-%m-%d"

    USE_DUMMY_DATASET: bool = False
    USE_DATA_FILL: bool = True
    METHOD: str = "from_data"

    PM25_MEDIAN: int = 15
    PM25_SIGMA: float = 0.8

    NO2_MEDIAN: int = 30
    NO2_SIGMA: float = 0.7

    CO2_MEAN: int = 420
    CO2_STD: int = 50

    DUPLICATION_ERROR: str = '23505'
    DELETE_PREV_TABLES: bool = False

    DEFAULT_RETRIES: int = 3
    DEFAULT_DELAY: int = 3

    DB: str = "prepSQL"
    SCHEME: str = "rolling_exercise"

    DB_USER: str
    DB_PASSWORD: str
    DATA_PATH: str

    class Config:
        env_file = ".env"

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@localhost/{self.DB}"


settings = Settings()
