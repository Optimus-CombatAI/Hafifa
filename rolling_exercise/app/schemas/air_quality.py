from datetime import date

from pydantic import BaseModel, Field, ConfigDict


class AirQualityRow(BaseModel):
    date: date
    city: str = Field(min_length=1, max_length=100)
    pm25: float
    no2: float
    co2: float

class AqiResult(BaseModel):
    aqi: float
    aqi_level: str
    is_alert: bool

class AirQualityMeasurementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)#convert sqlalchemy object to json
    date:date
    city:str = Field(min_length=1, max_length=100)
    pm25:float
    no2:float
    co2:float
    aqi:float
    aqi_level:str

class CityAqiAverageOut(BaseModel):
    city: str
    average_aqi: float