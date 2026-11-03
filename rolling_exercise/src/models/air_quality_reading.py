import datetime

from pydantic import BaseModel, ConfigDict, Field


class AirQualityReading(BaseModel):
    """One validated measurement of a city's pollutants on a given day."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    date: datetime.date
    city: str = Field(min_length=1)
    pm25: float = Field(ge=0, allow_inf_nan=False)
    no2: float = Field(ge=0, allow_inf_nan=False)
    co2: float = Field(ge=0, allow_inf_nan=False)
