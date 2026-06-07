from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env",extra="ignore")
    database_url:str
    alert_aqi_threshold: int

settings = Settings()   
