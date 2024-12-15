import math

import pydantic
import datetime as dt


class AirQualityBase(pydantic.BaseModel):
    date: dt.date
    city: str = pydantic.Field(min_length=1, description="City name cannot be empty")
    pm2_5: float = pydantic.Field(gt=0, description='PM2.5 concentration must be above or equal to 0')
    no2: float = pydantic.Field(gt=0, description='NO2 concentration must be above or equal to 0')
    co2: float = pydantic.Field(gt=0, description='CO2 concentration must be above or equal to 0')


class AirQualityResponse(AirQualityBase):
    aqi: float
    aqi_level: str
    id: int

    class Config:
        orm_mode = True


