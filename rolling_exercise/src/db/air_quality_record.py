import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.alert import Alert


class AirQualityRecord(Base):
    __tablename__ = "air_quality_records"
    __table_args__ = (UniqueConstraint("date", "city"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date]
    city: Mapped[str]
    pm25: Mapped[float]
    no2: Mapped[float]
    co2: Mapped[float]
    aqi: Mapped[float]
    aqi_level: Mapped[str]

    alert: Mapped["Alert | None"] = relationship(back_populates="air_quality_record")
