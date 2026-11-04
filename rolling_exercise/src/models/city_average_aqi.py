from pydantic import BaseModel


class CityAverageAqi(BaseModel):
    city: str
    average_aqi: float
