from datetime import date as DateType

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Date, Float,Integer,String

from app.db.session import Base

class AirQualityMeasurement(Base):
    __tablename__ = "air_quality_measurements"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    date: Mapped[DateType] = mapped_column(Date,index=True,nullable=False)
    city: Mapped[str] = mapped_column(String(100),index=True,nullable=False)
    pm25: Mapped[float] = mapped_column(Float,nullable=False)
    no2: Mapped[float] = mapped_column(Float,nullable=False)
    co2: Mapped[float] = mapped_column(Float,nullable=False)
    aqi: Mapped[float] = mapped_column(Float,nullable=False)
    aqi_level: Mapped[str] = mapped_column(String(50),nullable=False)
