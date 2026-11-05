import datetime

from pydantic import BaseModel, ConfigDict


class AqiHistoryEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: datetime.date
    aqi: float
    aqi_level: str
