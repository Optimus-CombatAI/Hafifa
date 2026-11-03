from pydantic import BaseModel


class AqiResult(BaseModel):
    aqi: float
    aqi_level: str
