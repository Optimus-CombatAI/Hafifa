import pydantic
import datetime


class AlertBase(pydantic.BaseModel):
    date: datetime.date
    city: str
    aqi: float
    aqi_level: str


class Alert(AlertBase):
    id: int

    class Config:
        orm_mode = True


